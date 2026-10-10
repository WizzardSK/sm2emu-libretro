// SPDX-License-Identifier: BSD-3-Clause
#pragma once

#include <string>
#include <string_view>
#include <vector>

namespace sm2::libretro::network {

struct Choice {
    std::string key;
    std::string label;
};

struct ManagedValue {
    std::string_view suffix;
    std::string key;
};

[[nodiscard]] std::vector<Choice> choices(std::string_view catalog,
                                          unsigned max_cabinets);
[[nodiscard]] std::vector<ManagedValue> managed_values(std::string_view catalog,
                                                       unsigned cabinets,
                                                       std::string_view preset);

}  // namespace sm2::libretro::network
