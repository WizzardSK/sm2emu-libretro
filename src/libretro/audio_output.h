// SPDX-License-Identifier: BSD-3-Clause
#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <span>

namespace sm2::libretro {
// Upstream 5e77a08's 5 Hz output DC blocker, independent of SDL/device ownership.
struct OutputDcBlocker {
    std::array<float, 2> previous_input{};
    std::array<float, 2> previous_output{};
    void reset() { previous_input = {}; previous_output = {}; }
    bool valid() const {
        for (unsigned ch=0; ch<2; ++ch)
            if (!std::isfinite(previous_input[ch]) || !std::isfinite(previous_output[ch])
                || std::abs(previous_input[ch]) > 32768.0f
                || std::abs(previous_output[ch]) > 131072.0f) return false;
        return true;
    }
    void process(std::span<int16_t> samples, unsigned sample_rate) {
        const float pole = 1.0f - 2.0f * 3.14159265f * 5.0f / static_cast<float>(sample_rate);
        for (size_t i=0; i<samples.size(); ++i) {
            const size_t ch=i%2;
            const float input=static_cast<float>(samples[i]);
            const float output=input-previous_input[ch]+pole*previous_output[ch];
            previous_input[ch]=input; previous_output[ch]=output;
            samples[i]=static_cast<int16_t>(std::clamp(output,-32768.0f,32767.0f));
        }
    }
};
}
