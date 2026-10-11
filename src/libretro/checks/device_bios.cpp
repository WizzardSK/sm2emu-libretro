// SPDX-License-Identifier: BSD-3-Clause
// Synthetic archives exercise frontend-supplied device lookup without ROMs.
#include "rom/game_db.h"
#include "rom/rom_loader.h"

#include <miniz.h>

#include <chrono>
#include <cstdio>
#include <filesystem>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {
namespace fs = std::filesystem;

void require(bool condition, const char* message)
{
    if (!condition) throw std::runtime_error(message);
}

void write_zip(const fs::path& path,
               const std::vector<std::pair<std::string, std::string>>& files)
{
    mz_zip_archive zip{};
    require(mz_zip_writer_init_file(&zip, path.string().c_str(), 0) == MZ_TRUE,
            "Cannot create synthetic archive");
    for (const auto& [name, data] : files)
        require(mz_zip_writer_add_mem(&zip, name.c_str(), data.data(), data.size(), 0) == MZ_TRUE,
                "Cannot add synthetic file");
    require(mz_zip_writer_finalize_archive(&zip) == MZ_TRUE,
            "Cannot finalize synthetic archive");
    mz_zip_writer_end(&zip);
}

void expect_bios(const sm2::rom::GameDatabase& database, const fs::path& game,
                 const fs::path& devices, sm2::u8 expected,
                 const char* selected = "fixture")
{
    const auto result = sm2::rom::RomLoader::load(
        database, game.string(), selected, false, devices.string());
    require(result.has_value(), "Synthetic game did not load");
    const auto bios = result->roms.region("ioboard");
    require(bios.size() == 1 && bios[0] == expected,
            "Wrong device archive took precedence");
}
}  // namespace

int main()
{
    const fs::path root = fs::temp_directory_path() /
        ("sm2-device-bios-" + std::to_string(
            std::chrono::steady_clock::now().time_since_epoch().count()));
    try {
        require(fs::create_directories(root / "system"), "Cannot create test directory");
        fs::create_directories(root / "roms");
        const fs::path game = root / "roms" / "fixture.zip";
        const fs::path sibling = root / "roms" / "device.zip";
        const fs::path shared = root / "system" / "device.zip";
        write_zip(game, {{"program.bin", "P"}, {"bios.bin", "G"}});
        write_zip(sibling, {{"bios.bin", "L"}});
        write_zip(shared, {{"bios.bin", "S"}});

        sm2::rom::GameDatabase database;
        require(database.load_from_string(R"(<games>
          <game name="fixture" board="model2">
            <title>Fixture</title>
            <devices><device name="device"/></devices>
            <roms>
              <region name="maincpu" size="1"><file name="program.bin" offset="0"/></region>
              <region name="ioboard" size="1"><file name="bios.bin" offset="0"/></region>
            </roms>
          </game>
          <game name="clone" parent="fixture" board="model2">
            <title>Clone</title>
            <roms><region name="maincpu" size="1"><file name="clone.bin" offset="0"/></region></roms>
          </game>
        </games>)"), "Cannot parse synthetic game database");

        expect_bios(database, game, root / "system", 'S');
        fs::remove(shared);
        expect_bios(database, game, root / "system", 'L');
        fs::remove(sibling);
        expect_bios(database, game, root / "system", 'G');
        // A split archive still identifies by its chips, independently of filename.
        const fs::path renamed = root / "roms" / "renamed.zip";
        write_zip(renamed, {{"program.bin", "P"}});
        write_zip(shared, {{"bios.bin", "S"}});
        expect_bios(database, renamed, root / "system", 'S', "");
        fs::remove(shared);
        require(!sm2::rom::RomLoader::load(database, renamed.string(), "fixture",
                    false, (root / "system").string()),
                "Missing required split firmware must fail");
        write_zip(sibling, {{"bios.bin", "L"}});
        expect_bios(database, renamed, root / "system", 'L');

        const fs::path clone = root / "roms" / "clone.zip";
        write_zip(clone, {{"clone.bin", "C"}});
        expect_bios(database, clone, root / "system", 'L', "clone");
        fs::remove(sibling);
        expect_bios(database, clone, root / "system", 'G', "clone");
        fs::remove(game);
        // The system directory supplies device firmware, never parent game ROMs.
        write_zip(root / "system" / "fixture.zip", {{"program.bin", "P"}, {"bios.bin", "G"}});
        require(!sm2::rom::RomLoader::load(database, clone.string(), "clone", false,
                    (root / "system").string()), "System directory must not supply parent archives");
        // Equal chip sets may differ only in program patches. Resolve exact
        // score ties by archive name; preserve renamed-content recognition.
        sm2::rom::GameDatabase tied;
        require(tied.load_from_string(R"(<games>
          <game name="main" board="model2"><title>Main</title><roms>
            <region name="maincpu" size="4"><file name="same.bin" offset="0"/>
              <patch offset="0" value="0x41414141"/></region>
          </roms></game>
          <game name="relay" board="model2"><title>Relay</title><roms>
            <region name="maincpu" size="4"><file name="same.bin" offset="0"/></region>
          </roms></game>
        </games>)"), "Cannot parse tied-set database");
        const auto relay = root / "roms" / "relay.zip";
        write_zip(relay, {{"same.bin", "RRRR"}});
        const auto selected = sm2::rom::RomLoader::load(tied, relay.string(), "", false);
        require(selected && selected->game.name == "relay"
                    && selected->roms.region("maincpu")[0] == 'R',
                "Named Relay must not receive Main patches");
        const auto forced = sm2::rom::RomLoader::load(tied, relay.string(), "main", false);
        require(forced && forced->game.name == "main"
                    && forced->roms.region("maincpu")[0] == 'A',
                "Explicit selection must retain precedence");
        const auto renamed_tie = root / "roms" / "unknown.zip";
        fs::copy_file(relay, renamed_tie);
        const auto fallback = sm2::rom::RomLoader::load(tied, renamed_tie.string(), "", false);
        require(fallback && fallback->game.name == "main",
                "Unnamed tie must preserve catalogue order");
        // Main keeps its named, CRC-verified program identity while its corrected
        // audio chips load locally first, falling back to the split parent.
        // Old Relay audio chips are not part of the Main definition.
        sm2::rom::GameDatabase parent_audio;
        require(parent_audio.load_from_string(R"(<games>
          <game name="slave" board="model2"><roms>
            <region name="maincpu" size="4"><file name="parent.bin" offset="0" crc="0xf5f2e160"/></region>
            <region name="audiocpu" size="2" stride="2" chunk="2" byte_swap="true"><file name="slave-sound.bin" offset="0" crc="0x8cc7184c"/></region>
            <region name="samples" size="4"><file name="slave-samples.bin" offset="0" crc="0xf5f2e160"/></region>
          </roms></game>
          <game name="main" parent="slave" board="model2"><roms>
            <region name="maincpu" size="4"><file name="program.bin" offset="0" crc="0x2290ede5"/><patch offset="0" value="0x41414141"/></region>
            <region name="audiocpu" size="2" stride="2" chunk="2" byte_swap="true"><file name="slave-sound.bin" offset="0" crc="0x8cc7184c"/></region>
            <region name="samples" size="4"><file name="slave-samples.bin" offset="0" crc="0xf5f2e160"/></region>
          </roms></game>
          <game name="relay" parent="slave" board="model2"><roms>
            <region name="maincpu" size="4"><file name="program.bin" offset="0" crc="0x2290ede5"/></region>
            <region name="audiocpu" size="2"><file name="relay-sound.bin" offset="0" crc="0xe2db199b"/></region>
            <region name="samples" size="4"><file name="relay-samples.bin" offset="0" crc="0x2290ede5"/></region>
          </roms></game>
        </games>)"), "Cannot parse parent audio fixture");
        const auto main_archive = root / "roms" / "main.zip";
        const auto slave_archive = root / "roms" / "slave.zip";
        const std::vector<std::pair<std::string, std::string>> original_chips{
            {"program.bin", "RRRR"}, {"relay-sound.bin", "rr"}, {"relay-samples.bin", "RRRR"}};
        write_zip(main_archive, original_chips);
        write_zip(slave_archive, {{"slave-sound.bin", "ss"}, {"slave-samples.bin", "SSSS"}});
        const auto corrected = sm2::rom::RomLoader::load(parent_audio, main_archive.string());
        require(corrected && corrected->game.name == "main"
                    && corrected->roms.region("maincpu")[0] == 'A'
                    && corrected->roms.region("audiocpu")[0] == 's'
                    && corrected->roms.region("samples")[0] == 'S'
                    && corrected->game.region("audiocpu")->byte_swap,
                "Named Main program must retain patches and assemble the matched parent sound layout");
        write_zip(relay, original_chips);
        const auto unaffected = sm2::rom::RomLoader::load(parent_audio, relay.string());
        require(unaffected && unaffected->game.name == "relay"
                    && unaffected->roms.region("maincpu")[0] == 'R'
                    && unaffected->roms.region("audiocpu")[0] == 'r',
                "Relay must retain its original sound regions");
        write_zip(slave_archive, {{"slave-sound.bin", "ss"}, {"slave-samples.bin", "BAD!"}});
        require(!sm2::rom::RomLoader::load(parent_audio, main_archive.string()),
                "Corrupt required parent sound must fail CRC lookup without Relay fallback");
        fs::remove(slave_archive);
        require(!sm2::rom::RomLoader::load(parent_audio, main_archive.string()),
                "Missing parent sound must not silently use unsupported Relay audio");
        std::vector<std::pair<std::string, std::string>> embedded_chips{{"program.bin", "RRRR"}};
        embedded_chips.emplace_back("slave-sound.bin", "ss");
        embedded_chips.emplace_back("slave-samples.bin", "SSSS");
        write_zip(main_archive, embedded_chips);
        const auto embedded = sm2::rom::RomLoader::load(parent_audio, main_archive.string());
        require(embedded && embedded->game.name == "main"
                    && embedded->roms.region("samples")[0] == 'S',
                "Local corrected Main audio must work without old Relay chips or a parent archive");
        write_zip(slave_archive, {{"slave-sound.bin", "BAD!"}, {"slave-samples.bin", "BAD!"}});
        require(sm2::rom::RomLoader::load(parent_audio, main_archive.string()).has_value(),
                "Correct Main-local audio must take precedence over a corrupt parent");
        // A matching filename cannot select a set with incompatible program CRCs.
        write_zip(main_archive, {{"parent.bin", "SSSS"}, {"slave-sound.bin", "ss"}, {"slave-samples.bin", "SSSS"}});
        const auto wrong_name = sm2::rom::RomLoader::load(parent_audio, main_archive.string());
        require(wrong_name && wrong_name->game.name == "slave",
                "Filename preference must require matching main program chips");
        sm2::rom::GameDatabase reconstruction;
        require(reconstruction.load_from_string(R"(<games>
          <game name="slave" board="model2"><roms>
            <region name="samples" size="4"><file name="slave-samples.bin" offset="0" crc="0xf5f2e160"/></region>
          </roms></game>
          <game name="main" parent="slave" rom_fallback="relay" board="model2"><roms>
            <region name="maincpu" size="4"><file name="program.bin" offset="0" crc="0x2290ede5"/><patch offset="0" value="0x41414141"/></region>
          </roms></game>
        </games>)"), "Cannot parse reconstructed archive fixture");
        fs::remove(main_archive);
        write_zip(slave_archive, {{"slave-samples.bin", "SSSS"}});
        const auto absent = sm2::rom::RomLoader::load(reconstruction, main_archive.string());
        require(absent && absent->game.name == "main"
                    && absent->roms.region("maincpu")[0] == 'A'
                    && absent->roms.region("samples")[0] == 'S',
                "Absent reconstructed archive must retain identity, patches and parent data");
        write_zip(main_archive, {});
        require(sm2::rom::RomLoader::load(reconstruction, main_archive.string()).has_value(),
                "Empty content entry must resolve the declared donor");
        fs::remove(relay);
        require(!sm2::rom::RomLoader::load(reconstruction, main_archive.string()),
                "Missing donor program must fail rather than fill required data");
        write_zip(main_archive, {{"program.bin", "RRRR"}, {"slave-samples.bin", "SSSS"}});
        write_zip(relay, {{"program.bin", "BAD!"}});
        require(sm2::rom::RomLoader::load(reconstruction, main_archive.string()).has_value(),
                "Valid local chips must work without a valid donor");
        fs::remove(main_archive);
        require(!sm2::rom::RomLoader::load(reconstruction, main_archive.string()),
                "Corrupt fallback program must fail CRC verification");
        fs::remove_all(root);
        return 0;
    } catch (const std::exception& error) {
        std::fprintf(stderr, "Device BIOS check failed: %s\n", error.what());
        fs::remove_all(root);
        return 1;
    }
}
