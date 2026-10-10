// SPDX-License-Identifier: BSD-3-Clause
#include "cpu/i960/i960.h"
#include "hw/model2_area_timing.h"
#include "core/archive.h"
#include <array>
#include <bit>
#include <cstdio>
#include <cstring>
#include <stdexcept>
#include <vector>
using namespace sm2;
namespace {
void check(bool value,const char* text) {if(!value)throw std::runtime_error(text);}
struct Memory : cpu::Bus {
    std::array<u8,8192> data{};
    cpu::i960::I960* processor=nullptr;
    s32 waits=0;
    unsigned accesses=0;
    unsigned fetches=0;
    u8 read8(u32 a) override {return data.at(a);}
    u16 read16(u32 a) override {u16 v;std::memcpy(&v,&data.at(a),2);return v;}
    u32 read32(u32 a) override {
        if(processor && a>=4096) {processor->add_wait_cycles(waits);++accesses;}
        u32 v;std::memcpy(&v,&data.at(a),4);return v;
    }
    u32 fetch32(u32 a) override {++fetches;u32 v;std::memcpy(&v,&data.at(a),4);return v;}
    void write8(u32 a,u8 v) override {data.at(a)=v;}
    void write16(u32 a,u16 v) override {std::memcpy(&data.at(a),&v,2);}
    void write32(u32 a,u32 v) override {std::memcpy(&data.at(a),&v,4);}
};
struct Program {
    Memory memory;
    cpu::i960::I960 cpu{memory};
    u32 next=256;
    Program() {memory.write32(4,64);memory.write32(12,256);memory.write32(88,2048);cpu.reset();memory.processor=&cpu;}
    void instruction(u32 op) {memory.write32(next,op);next+=4;}
    void constant(unsigned reg,u32 value) {instruction(0x8c003000u|(reg<<19));instruction(value);}
    void execute() {
        // Each run retires one complete instruction, including its wait cost.
        while(cpu.ip()<next) {cpu.run(1);check(!cpu.faulted(),"Synthetic i960 program must not fault");}
    }
};
u32 regop(unsigned major,unsigned minor,unsigned dst,unsigned src1,unsigned src2=0) {
    return (major<<24)|(minor<<7)|(dst<<19)|(src2<<14)|src1;
}
}
int main() {
    try {
        for(unsigned bytes : {0u,3u,4u,7u,8u}) {
            Program p;p.constant(16,123);
            p.cpu.bind_fetch_window(0,256,p.memory.data.data()+256,bytes,8);
            p.execute();
            check(p.cpu.reg(16)==123,"Bounded instruction and operand fetches retain their values");
            check(p.memory.fetches==(bytes<4?2u:bytes<8?1u:0u),
                  "Incomplete words fall back to the bus at the fetch-window boundary");
        }
        {
            Program p;p.constant(16,123);
            p.cpu.bind_fetch_window(0,256,p.memory.data.data()+256,8,4);
            p.execute();
            check(p.memory.fetches==1,"Address window limits apply even with a larger backing buffer");
        }
        {
            Program p;p.constant(16,123);
            p.cpu.bind_fetch_window(0,256,p.memory.data.data()+256,4,4);
            p.cpu.bind_fetch_window(1,260,p.memory.data.data()+260,4,4);
            std::vector<u8> saved;Archive save(saved);p.cpu.serialize(save);
            p.execute();
            check(p.cpu.reg(16)==123 && p.memory.fetches==0,"Both instruction-fetch windows are active");
            // Restore into a different CPU and backing allocation: saved host
            // pointers must not replace the bindings supplied by its machine.
            Program restored;restored.constant(16,456);
            restored.cpu.bind_fetch_window(0,256,restored.memory.data.data()+256,8,8);
            Archive load(saved.data(),saved.size());restored.cpu.serialize(load);
            check(!load.failed(),"Fetch bindings add no serialized CPU fields");
            restored.execute();
            check(restored.cpu.reg(16)==456 && restored.memory.fetches==0,
                  "State restore retains the destination machine's live fetch bindings");
            restored.memory.write32(260,789);restored.cpu.reset();restored.execute();
            check(restored.cpu.reg(16)==789 && restored.memory.fetches==0,
                  "Reset retains fetch bindings and work-RAM writes are immediately visible");
            restored.cpu.bind_fetch_window(0,256,nullptr,8,8);
            restored.cpu.reset();restored.execute();
            check(restored.memory.fetches==2,"Unbinding a window restores bus fetches");
        }
        for(bool even : {false,true}) {
            Program p;p.cpu.set_round_nearest_even(even);
            p.constant(16,std::bit_cast<u32>(2.5f));
            p.instruction(regop(0x6c,0,17,16));
            p.constant(18,std::bit_cast<u32>(-2.5f));
            p.instruction(regop(0x6c,0,19,18));p.execute();
            check(p.cpu.reg(17)==(even?2u:3u),"Positive rounding convention is preserved");
            check(p.cpu.reg(19)==u32(even?-2:-3),"Negative rounding convention is preserved");
        }
        for(unsigned carry : {0u,2u}) {
            Program p;p.constant(16,7);p.constant(17,10);
            p.instruction(regop(0x64,5,20,7,carry)|0x1800); // modac literal mask/value
            p.instruction(regop(0x5b,2,18,16,17));p.execute();
            check(p.cpu.reg(18)==(carry?3u:2u),"subc includes inverted borrow correctly");
            check((p.cpu.ac()&7)==2,"subc sets the carry and clears other condition bits");
        }
        for(unsigned encoding : {1u,9u}) {
            Program p;
            // movre literal 1.0 -> fp0 -> three integer registers -> fp1.
            p.instruction(regop(0x6e,encoding,0,0x16)|0x2800);
            p.instruction(regop(0x6e,encoding,16,0)|0x0800);
            p.instruction(regop(0x6e,encoding,1,16)|0x2000);
            p.instruction(regop(0x6c,0,20,1)|0x0800);p.execute();
            check(p.cpu.reg(16)==0 && p.cpu.reg(17)==0x80000000 && p.cpu.reg(18)==0x3fff,
                  "movre uses the Intel 80-bit extended register image");
            check(p.cpu.reg(20)==1,"Both movre encodings restore the floating-point register");
        }
        {
            Program p;p.constant(16,u32(-50000));p.constant(17,100000);
            p.instruction(regop(0x74,9,18,16,17));p.execute();
            check(p.cpu.reg(18)==0,"modi handles operands whose product would overflow");
        }
        std::array<u8,0x38> regs{};
        for(auto [address,offset] : std::array<std::pair<u32,unsigned>,10>{{
            {0,0},{0x500000,8},{0x900000,4},{0x1800000,0x1c},{0x1a00000,0x20},
            {0x1c00000,0x24},{0x1c80000,0x28},{0x1d00000,0x2c},{0x1d80000,0x30},{0x2000000,0x34}}}) {
            regs.fill(0);regs[offset]=0x10;
            check(hw::area_wait_cycles(address,regs)==12,"Each programmed memory area charges four waits");
            regs[offset]|=0x40;
            check(hw::area_wait_cycles(address,regs)==0,"DRAM accesses bypass programmed area waits");
        }
        for(auto [setting,cycles] : std::array<std::pair<u8,s32>,7>{{{1,0},{2,3},{4,6},{8,9},{16,12},{32,0},{0,0}}}) {
            regs.fill(setting);check(hw::area_wait_cycles(0,regs)==cycles,"Wait codes match Sega's table");
        }
        check(hw::area_wait_cycles(0x1000000,regs)==0,"Tile waits use their separate device path");
        check(hw::area_wait_cycles(0x2000000,{})==0,"Short register image is safe");
        auto retired=[](s32 waits) {
            Program p;p.memory.waits=waits;p.memory.write32(4096,123);
            p.instruction(0x90803000);p.instruction(4096); // ld absolute -> g0
            p.instruction(0x08fffff8); // branch to the load
            p.cpu.run(1000);check(!p.cpu.faulted() && p.memory.accesses>0,"Load loop executes");
            return p.cpu.instructions();
        };
        check(retired(12)<retired(0),"Bus wait cycles reduce retired instructions without charging fetches");
        std::puts("i960 fetch, opcode, rounding and area timing checks passed");return 0;
    } catch(const std::exception& e) {std::fprintf(stderr,"i960 check failed: %s\n",e.what());return 1;}
}
