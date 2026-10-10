// SPDX-License-Identifier: BSD-3-Clause
#include "netpacket.h"

#include "hw/m2comm.h"
#include "core/archive.h"

#include <algorithm>
#include <array>
#include <cstdio>
#include <deque>
#include <memory>
#include <optional>
#include <span>
#include <stdexcept>
#include <vector>

using namespace sm2;

namespace {

void check(bool okay, const char* message)
{
    if (!okay) throw std::runtime_error(message);
}

struct RingBus {
    explicit RingBus(unsigned cabinets) : incoming(cabinets) {}
    std::vector<std::deque<std::vector<u8>>> incoming;
};

class RingTransport final : public hw::CommTransport {
public:
    RingTransport(std::shared_ptr<RingBus> bus, unsigned cabinet)
        : m_bus(std::move(bus)), m_cabinet(cabinet) {}

    [[nodiscard]] bool ready() const override { return true; }
    void send(std::span<const u8> frame) override
    {
        const unsigned successor = (m_cabinet + 1) % m_bus->incoming.size();
        m_bus->incoming[successor].emplace_back(frame.begin(), frame.end());
    }
    [[nodiscard]] std::optional<std::vector<u8>> recv() override
    {
        auto& incoming = m_bus->incoming[m_cabinet];
        if (incoming.empty()) return std::nullopt;
        std::vector<u8> frame = std::move(incoming.front());
        incoming.pop_front();
        return frame;
    }
    [[nodiscard]] bool connected() const override { return true; }
    void reset() override { m_bus->incoming[m_cabinet].clear(); }

private:
    std::shared_ptr<RingBus> m_bus;
    unsigned m_cabinet;
};

retro_netpacket_callback* captured_callbacks = nullptr;
std::vector<u8> sent_packet;
int sent_flags = 0;
u16 sent_peer = 0xffff;

bool environment(unsigned command, void* data)
{
    if (command != RETRO_ENVIRONMENT_SET_NETPACKET_INTERFACE) return false;
    captured_callbacks = static_cast<retro_netpacket_callback*>(data);
    return true;
}

void RETRO_CALLCONV send_packet(int flags, const void* data, std::size_t size,
                                u16 client_id)
{
    sent_flags = flags;
    sent_peer = client_id;
    const auto* bytes = static_cast<const u8*>(data);
    sent_packet.assign(bytes, bytes + size);
}

void check_model2_ring(unsigned cabinet_count)
{
    auto bus = std::make_shared<RingBus>(cabinet_count);
    std::vector<std::unique_ptr<std::array<u8, hw::M2Comm::kSharedSize>>> ram;
    std::vector<std::unique_ptr<hw::M2Comm>> cabinets;
    for (unsigned cabinet = 0; cabinet < cabinet_count; ++cabinet) {
        ram.push_back(std::make_unique<std::array<u8, hw::M2Comm::kSharedSize>>());
        cabinets.push_back(std::make_unique<hw::M2Comm>());
        cabinets.back()->attach_shared(*ram.back());
        cabinets.back()->set_transport(std::make_unique<RingTransport>(bus, cabinet));
        cabinets.back()->reset();
        cabinets.back()->fg_write(cabinet == 0 ? 1 : 0);
        cabinets.back()->cn_write(1);
    }

    for (unsigned frame = 0; frame < 600; ++frame)
        for (auto& cabinet : cabinets) cabinet->vblank();

    std::vector<unsigned> ids;
    for (const auto& cabinet : cabinets) {
        check(cabinet->link_alive(), "Communication board did not establish the ring");
        check(cabinet->link_count() == cabinet_count,
              "Model 2 ring reported an unexpected cabinet count");
        ids.push_back(cabinet->link_id());
    }
    std::sort(ids.begin(), ids.end());
    for (unsigned cabinet = 0; cabinet < cabinet_count; ++cabinet)
        check(ids[cabinet] == cabinet + 1,
              "Model 2 ring assigned duplicate or missing cabinet IDs");

    for (unsigned cabinet = 0; cabinet < cabinet_count; ++cabinet) {
        (*ram[cabinet])[0x2000] = static_cast<u8>(0x40 + cabinet);
        (*ram[cabinet])[0x2001] = static_cast<u8>(0xa0 + cabinet);
    }
    for (unsigned frame = 0; frame < cabinet_count + 4; ++frame)
        for (auto& cabinet : cabinets) cabinet->vblank();
    for (unsigned cabinet = 0; cabinet < cabinet_count; ++cabinet) {
        const unsigned predecessor = (cabinet + cabinet_count - 1) % cabinet_count;
        check((*ram[cabinet])[0x21c0] == 0x40 + predecessor
                  && (*ram[cabinet])[0x21c1] == 0xa0 + predecessor,
              "A cabinet did not receive its predecessor's communication payload");
    }
}

void check_power_sled_ring(bool generic_relay)
{
    auto bus = std::make_shared<RingBus>(3);
    std::array<std::array<u8, hw::M2Comm::kSharedSize>, 3> ram{};
    std::array<hw::M2Comm, 3> cabinets;
    for (unsigned i = 0; i < 3; ++i) {
        cabinets[i].attach_shared(ram[i]);
        cabinets[i].set_transport(std::make_unique<RingTransport>(bus, i));
        cabinets[i].set_frame_offset(0x180);
        cabinets[i].reset();
        cabinets[i].cn_write(1);
        // Observed Power Sled programs use shared role 2 on all three units;
        // Main sets FG. Also cover the generic non-counted Relay simulation.
        cabinets[i].fg_write(i == 0 ? 1 : 0);
        ram[i][1] = generic_relay && i == 1 ? 0 : 2;
    }
    for (unsigned frame = 0; frame < 600; ++frame)
        for (auto& cabinet : cabinets) cabinet.vblank();
    for (unsigned i = 0; i < 3; ++i) {
        check(cabinets[i].link_alive(), "Power Sled ring did not establish");
        check(cabinets[i].link_count() == (generic_relay ? 2u : 3u),
              "Power Sled enumerated node count mismatch");
        check(cabinets[i].link_id() == (i == 0 ? 1 : i == 1 ? (generic_relay ? 0 : 3) : 2),
              "Power Sled Main/Relay/Slave identity mismatch");
    }
    ram[0][0x2000] = 0x42;
    ram[1][0x2000] = 0x65;
    ram[2][0x2000] = 0x73;
    for (unsigned frame = 0; frame < 12; ++frame)
        for (auto& cabinet : cabinets) cabinet.vblank();
    check(ram[2][0x2180] == (generic_relay ? 0x42 : 0x65) && ram[0][0x2180] == 0x73,
          "Power Sled payload not delivered through Relay at offset 0x180");
}

void check_power_sled_handshake()
{
    libretro::NetpacketTransport transport;
    transport.configure("powsled", 3, 1);
    captured_callbacks->start(0, send_packet, nullptr);
    check(captured_callbacks->connected(1) && captured_callbacks->connected(2),
          "Power Sled participants rejected");
    check(!transport.ready(), "Power Sled ready before program roles known");
    auto hello = sent_packet;
    check(hello.size() == 15 && hello[14] == 1, "Main program identity missing");
    // Two Main programs must not form a valid Main/Relay/Slave roster.
    captured_callbacks->receive(hello.data(), hello.size(), 1);
    hello[14] = 3;
    captured_callbacks->receive(hello.data(), hello.size(), 2);
    check(!transport.ready(), "Duplicate Main program accepted");
    hello[14] = 2;
    captured_callbacks->receive(hello.data(), hello.size(), 1);
    check(transport.ready(), "Valid Power Sled program roster rejected");
    captured_callbacks->stop();
}

void check_counted_relay_ring()
{
    auto bus = std::make_shared<RingBus>(3);
    std::array<std::array<u8, hw::M2Comm::kSharedSize>, 3> ram{};
    std::array<hw::M2Comm, 3> cabinets;
    for (unsigned i = 0; i < 3; ++i) {
        cabinets[i].attach_shared(ram[i]);
        cabinets[i].set_counted_relay(true);
        cabinets[i].set_transport(std::make_unique<RingTransport>(bus, i));
        cabinets[i].reset();
        cabinets[i].cn_write(1);
        cabinets[i].fg_write(i == 0 ? 1 : 0);
        ram[i][1] = i == 0 ? 1 : i == 1 ? 2 : 3;
    }
    for (unsigned frame = 0; frame < 600; ++frame)
        for (auto& cabinet : cabinets) cabinet.vblank();
    for (unsigned i = 0; i < 3; ++i) {
        check(cabinets[i].link_alive() && cabinets[i].link_count() == 3,
              "Counted Relay ring did not establish");
        check(cabinets[i].link_id() == (i == 0 ? 1 : i == 1 ? 3 : 2),
              "Counted Relay IDs violate native host range 1..count");
    }
    ram[0][0x2000] = 0x42;
    ram[1][0x2000] = 0x65;
    ram[2][0x2000] = 0x73;
    for (unsigned frame = 0; frame < 12; ++frame)
        for (auto& cabinet : cabinets) cabinet.vblank();
    check(ram[0][0x21c0] == 0x73 && ram[0][0x2380] == 0x65
          && ram[0][0x2540] == 0x42 && ram[2][0x21c0] == 0x65,
          "Counted Relay must include its own status and retain the preceding native slot train");
}

std::vector<u8> begin_handshake(libretro::NetpacketTransport& transport,
                                u16 local_id, unsigned cabinet_count)
{
    transport.configure("daytona", cabinet_count);
    captured_callbacks->start(local_id, send_packet, nullptr);
    if (local_id == 0)
        for (u16 peer = 1; peer < cabinet_count; ++peer)
            check(captured_callbacks->connected(peer), "Configured cabinet was rejected");
    check(!transport.ready(), "Cabinet became ready before peer hellos arrived");
    check(sent_peer == RETRO_NETPACKET_BROADCAST,
          "Handshake hello was not broadcast to all cabinets");
    return sent_packet;
}

void feed_hello(const std::vector<u8>& hello, u16 sender)
{
    captured_callbacks->receive(hello.data(), hello.size(), sender);
}

void check_host_adapter()
{
    libretro::NetpacketTransport transport;
    const std::vector<u8> hello = begin_handshake(transport, 0, 4);
    feed_hello(hello, 1);
    feed_hello(hello, 2);
    check(!transport.ready(), "Host became ready with an incomplete roster");
    feed_hello(hello, 3);
    check(transport.ready(), "Host did not become ready with four cabinets");
    check(!captured_callbacks->connected(4), "A fifth cabinet was accepted");

    const std::array<u8, 4> payload{0xff, 4, 0, 0};
    transport.send(payload);
    check(sent_peer == 1, "Host frame was not addressed to its ring successor");
    check((sent_flags & RETRO_NETPACKET_RELIABLE) != 0,
          "Communication board frame was not reliable");
    const std::vector<u8> frame = sent_packet;

    captured_callbacks->receive(frame.data(), frame.size(), 2);
    check(!transport.recv(), "Host accepted a frame from a non-predecessor cabinet");
    captured_callbacks->receive(frame.data(), frame.size(), 3);
    const auto received = transport.recv();
    check(received && *received == std::vector<u8>(payload.begin(), payload.end()),
          "Host did not receive the predecessor's communication frame");

    captured_callbacks->disconnected(2);
    check(!transport.ready(), "Disconnected roster remained ready");
    captured_callbacks->stop();
}

void check_client_adapter()
{
    libretro::NetpacketTransport transport;
    const std::vector<u8> hello = begin_handshake(transport, 2, 4);
    feed_hello(hello, 0);
    feed_hello(hello, 1);
    feed_hello(hello, 3);
    check(transport.ready(), "Client did not build the four-cabinet roster");

    const std::array<u8, 3> payload{0xfc, 1, 0};
    transport.send(payload);
    check(sent_peer == 3, "Client frame was not addressed to its ring successor");
    const std::vector<u8> frame = sent_packet;
    captured_callbacks->receive(frame.data(), frame.size(), 1);
    const auto received = transport.recv();
    check(received && *received == std::vector<u8>(payload.begin(), payload.end()),
          "Client did not receive its predecessor's communication frame");
    captured_callbacks->stop();
}

void check_nine_cabinet_capacity()
{
    libretro::NetpacketTransport transport;
    const std::vector<u8> hello = begin_handshake(transport, 0, 9);
    for (u16 peer = 1; peer < 9; ++peer) feed_hello(hello, peer);
    check(transport.ready(), "Nine-cabinet roster did not become ready");
    check(!captured_callbacks->connected(9), "A tenth cabinet was accepted");
    captured_callbacks->stop();
}

void check_mismatched_settings()
{
    libretro::NetpacketTransport transport;
    std::vector<u8> hello = begin_handshake(transport, 0, 2);
    hello[6] = 3;
    captured_callbacks->receive(hello.data(), hello.size(), 1);
    check(!transport.ready(), "Mismatched cabinet count completed the handshake");
    hello[6] = 2;
    captured_callbacks->receive(hello.data(), hello.size(), 1);
    check(transport.ready(), "Temporary cabinet-count mismatch blocked recovery");
    captured_callbacks->stop();
}

void check_burst_order_and_capacity()
{
    libretro::NetpacketTransport transport;
    const auto hello = begin_handshake(transport, 0, 2);
    feed_hello(hello, 1);
    check(transport.ready(), "Burst test roster did not become ready");
    for (unsigned index = 0; index < 512; ++index) {
        const std::array<u8, 2> payload{static_cast<u8>(index),
                                        static_cast<u8>(index >> 8)};
        transport.send(payload);
        captured_callbacks->receive(sent_packet.data(), sent_packet.size(), 1);
    }
    for (unsigned index = 0; index < 512; ++index) {
        const auto frame = transport.recv();
        check(frame && frame->size() == 2 && (*frame)[0] == static_cast<u8>(index)
                  && (*frame)[1] == static_cast<u8>(index >> 8),
              "Burst frame was lost or reordered");
    }
    check(!transport.recv(), "Burst left unexpected frames queued");

    for (unsigned index = 0; index < 1025; ++index) {
        const std::array<u8, 1> payload{static_cast<u8>(index)};
        transport.send(payload);
        captured_callbacks->receive(sent_packet.data(), sent_packet.size(), 1);
    }
    check(!transport.ready(), "Queue overflow did not stop the linked session");
    transport.configure("daytona", 2);
    feed_hello(hello, 1);
    check(transport.ready(), "Reconfigured session did not recover after overflow");
    captured_callbacks->stop();
}

void check_early_frames_do_not_block_roster()
{
    libretro::NetpacketTransport transport;
    const auto hello = begin_handshake(transport, 2, 3);
    std::vector<u8> frame = hello;
    frame[5] = 2;
    frame[12] = 1;
    frame.push_back(0xaa);
    for (unsigned index = 0; index < 1400; ++index)
        captured_callbacks->receive(frame.data(), frame.size(), 1);
    feed_hello(hello, 0);
    feed_hello(hello, 1);
    check(transport.ready(), "Early peer frames prevented the local roster from forming");
    check(!transport.recv(), "Early peer frames leaked into the completed ring");
    captured_callbacks->stop();
}

void check_repeated_hello_does_not_overflow()
{
    libretro::NetpacketTransport transport;
    auto hello = begin_handshake(transport, 2, 3);
    for (u8 type : {u8{1}, u8{3}}) {
        hello[5] = type;
        for (unsigned index = 0; index < 1400; ++index)
            feed_hello(hello, 0);
    }
    feed_hello(hello, 1);
    check(transport.ready(), "Repeated peer hellos filled the pending queue");
    captured_callbacks->stop();
}

void check_mismatched_game()
{
    libretro::NetpacketTransport transport;
    std::vector<u8> hello = begin_handshake(transport, 0, 2);
    hello[8] ^= 1;
    captured_callbacks->receive(hello.data(), hello.size(), 1);
    check(!transport.ready(), "Mismatched game completed the handshake");
    captured_callbacks->stop();
}

void check_known_peer_restarts()
{
    libretro::NetpacketTransport transport;
    auto request = begin_handshake(transport, 0, 2);
    check(request[5] == 3, "Waiting cabinet did not request peer identities");
    feed_hello(request, 1);
    check(transport.ready(), "Restart test roster did not form");
    auto reply = sent_packet;
    check(reply[5] == 1, "Identity request did not receive an ordinary reply");

    sent_packet.clear();
    feed_hello(reply, 1);
    check(transport.ready() && sent_packet.empty(),
          "Known peer reply triggered a broadcast echo");
    for (unsigned i = 0; i < 1400; ++i) feed_hello(request, 1);
    check(transport.ready() && !sent_packet.empty() && sent_packet[5] == 1,
          "Known peer restart request was ignored or overflowed");

    transport.configure("daytona", 2);
    check(!transport.ready(), "Reconfigured cabinet retained its old roster");
    feed_hello(reply, 1);
    check(transport.ready(), "Restarting cabinet rejected known peer identity");
    captured_callbacks->stop();
}

void check_netpacket_adapter()
{
    check(libretro::register_netpacket_interface(environment, nullptr),
          "Frontend rejected Netpacket registration");
    check(captured_callbacks != nullptr, "Netpacket callbacks were not registered");
    check_host_adapter();
    check_client_adapter();
    check_nine_cabinet_capacity();
    check_mismatched_settings();
    check_burst_order_and_capacity();
    check_early_frames_do_not_block_roster();
    check_repeated_hello_does_not_overflow();
    check_mismatched_game();
    check_known_peer_restarts();
    libretro::shutdown_netpacket_interface();
}

}  // namespace

int main()
{
    try {
        hw::LoopbackTransport local;
        const std::array<u8, 3> pending{1, 2, 3};
        local.send(pending);
        std::vector<u8> image;
        Archive writer(image);
        local.serialize(writer);
        check(!writer.failed(), "Local queue save");
        local.recv();
        local.send(std::array<u8, 1>{9});
        Archive reader(image.data(), image.size());
        local.serialize(reader);
        check(!reader.failed() && local.recv() == std::vector<u8>(pending.begin(), pending.end())
                  && !local.recv(), "Restore pending frames, discard future queue");
        for (unsigned i = 0; i <= hw::LoopbackTransport::kDepth; ++i) local.send(pending);
        check(!local.connected(), "Overflow state established");
        image.clear();
        Archive overflow_writer(image);
        local.serialize(overflow_writer);
        local.reset();
        Archive overflow_reader(image.data(), image.size());
        local.serialize(overflow_reader);
        check(!overflow_reader.failed() && !local.connected(), "Overflow state restored");
        const std::array<u8, 4> excessive{65, 0, 0, 0};
        Archive bad_count(excessive.data(), excessive.size());
        local.serialize(bad_count);
        check(bad_count.failed(), "Oversized queue rejected");
        const std::array<u8, 8> oversized_frame{1, 0, 0, 0, 1, 16, 0, 0};
        Archive bad_frame(oversized_frame.data(), oversized_frame.size());
        local.serialize(bad_frame);
        check(bad_frame.failed(), "Oversized local frame rejected");

        for (unsigned cabinets : {2u, 3u, 4u, 8u, 9u}) check_model2_ring(cabinets);
        check_power_sled_ring(false);
        check_power_sled_ring(true);
        check_counted_relay_ring();
        check_netpacket_adapter();
        check_power_sled_handshake();
        std::puts("SM2 Libretro Netpacket checks passed");
        return 0;
    } catch (const std::exception& error) {
        std::fprintf(stderr, "SM2 Libretro Netpacket check failed: %s\n", error.what());
        return 1;
    }
}
