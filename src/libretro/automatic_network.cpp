// SPDX-License-Identifier: BSD-3-Clause
#include "automatic_network.h"

#include <algorithm>
#include <charconv>

namespace sm2::libretro::network {
namespace {

bool is_car_role(std::string_view catalog)
{
    return catalog == "stcc" || catalog == "stcca" || catalog == "stccb"
        || catalog == "stcco" || catalog == "srallyc";
}

bool has_relay(std::string_view catalog)
{
    return is_car_role(catalog) || catalog == "manxtt" || catalog == "motoraid"
        || catalog == "motoraiddx";
}

unsigned playable_limit(std::string_view catalog, unsigned max_cabinets)
{
    if (is_car_role(catalog) || catalog == "manxtt" || catalog == "von")
        return max_cabinets - 1;
    return max_cabinets;
}

std::string_view role_key(std::string_view preset)
{
    return preset == "1" ? "master" : "slave";
}

}  // namespace

std::vector<Choice> choices(std::string_view catalog, unsigned max_cabinets)
{
    if (catalog.empty() || max_cabinets < 2) return {};
    if (catalog == "powsledr" || catalog == "vonr")
        return {{"relay", "Relay"}};
    if (catalog == "powsled" || catalog == "powsledm")
        return {{"1", "Silver"}, {"2", "Red"}, {"3", "Black"},
                {"0", "Disabled"}};
    const unsigned limit = playable_limit(catalog, max_cabinets);
    std::vector<Choice> result;
    result.push_back({"1", is_car_role(catalog) ? "Car 1 (Master)" : "Master (Cabinet 1)"});
    for (unsigned number = 2; number <= limit; ++number) {
        const std::string id = std::to_string(number);
        result.push_back({id, is_car_role(catalog)
            ? "Car " + id : "Slave (Cabinet " + id + ")"});
    }
    if (has_relay(catalog))
        result.push_back({"relay", catalog == "motoraid" || catalog == "motoraiddx"
            ? "Live (Relay)" : "Relay"});
    result.push_back({"0", "Disabled"});
    return result;
}

std::vector<ManagedValue> managed_values(std::string_view catalog,
                                        unsigned cabinets, std::string_view preset)
{
    if (preset.empty() || preset == "0") return {};
    if (catalog == "powsledr") return {};
    if (catalog == "powsled" || catalog == "powsledm") {
        if (preset == "1") return {{"ride_id", "silver"}};
        if (preset == "2") return {{"ride_id", "red"}};
        if (preset == "3") return {{"ride_id", "black"}};
        return {};
    }
    unsigned number = 1;
    if (preset != "relay") {
        const auto parsed = std::from_chars(preset.data(), preset.data() + preset.size(), number);
        if (parsed.ec != std::errc{} || parsed.ptr != preset.data() + preset.size()
            || number < 1 || number > 9 || std::to_string(number) != preset) return {};
    }
    const bool linked = cabinets > 1;
    if (!linked) {
        if (catalog == "daytona" || catalog == "daytonas")
            return {{"link_id", "single"}, {"car_number", "1"}};
        if (is_car_role(catalog))
            return {{"link_type", catalog == "srallyc" ? "notlink" : "stand_alone"}};
        if (catalog == "indy500" || catalog == "indy500d" || catalog == "motoraid"
            || catalog == "motoraiddx" || catalog == "waverunr")
            return {{"network_type", "stand_alone"}, {"cabinet_id", "1"}};
        if (catalog == "skisuprg")
            return {{"network_type", "no_link"}, {"cabinet_id", "1"}};
        if (catalog == "manxtt") return {{"link_type", "not_link"}};
        if (catalog == "sgt24h") return {{"link_type", "not_link"}};
        if (catalog == "overrev") return {{"link_max", "not_link"}};
        if (catalog == "von") return {{"network_link_attribute", "no_link"}};
        return {};
    }

    if (catalog == "daytona" || catalog == "daytonas")
        return {{"link_id", std::string(role_key(preset))},
                {"car_number", std::to_string(number)}};
    if (is_car_role(catalog))
        return {{"link_type", preset == "relay" ? "relay"
            : "car_" + std::to_string(number)}};
    if (catalog == "indy500" || catalog == "indy500d" || catalog == "motoraid"
        || catalog == "motoraiddx" || catalog == "waverunr" || catalog == "skisuprg")
        return {{"network_type", preset == "relay" ? "live"
            : std::string(role_key(preset))},
                {"cabinet_id", std::to_string(preset == "relay" ? cabinets : number)}};
    if (catalog == "manxtt")
        return {{"link_type", preset == "relay" ? "relay"
            : std::string(role_key(preset))}};
    if (catalog == "sgt24h")
        return {{"link_type", number == 1 ? "car_no1_master"
            : "car_no" + std::to_string(number) + "_slave"},
                {"link_max", std::to_string(cabinets)}};
    if (catalog == "overrev")
        return {{"link_type", number == 1 ? "master_carno_1"
            : "slave_carno_" + std::to_string(number)},
                {"link_max", std::to_string(cabinets) + "_links"}};
    if (catalog == "von")
        return {{"network_link_attribute", preset == "relay" ? "no_link"
            : std::string(role_key(preset))}};
    return {};
}

}  // namespace sm2::libretro::network
