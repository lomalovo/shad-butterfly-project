| run                          | count    |   photos |   errors |   mean_boxes |   zero_boxes |   one_box |   two_plus |
|:-----------------------------|:---------|---------:|---------:|-------------:|-------------:|----------:|-----------:|
| dino_butterfly               | multiple |       18 |        0 |        2.889 |        0.000 |     0.167 |      0.833 |
| dino_butterfly               | one      |      272 |        0 |        1.074 |        0.004 |     0.926 |      0.070 |
| dino_butterfly               | zero     |      110 |        0 |        1.536 |        0.055 |     0.636 |      0.309 |
| dino_butterfly_moth          | multiple |       18 |        0 |        2.667 |        0.000 |     0.222 |      0.778 |
| dino_butterfly_moth          | one      |      272 |        0 |        1.033 |        0.015 |     0.941 |      0.044 |
| dino_butterfly_moth          | zero     |      110 |        0 |        1.209 |        0.109 |     0.691 |      0.200 |
| dino_butterfly_moth__nms_off | multiple |       18 |        0 |        4.833 |        0.000 |     0.000 |      1.000 |
| dino_butterfly_moth__nms_off | one      |      272 |        0 |        2.710 |        0.015 |     0.026 |      0.960 |
| dino_butterfly_moth__nms_off | zero     |      110 |        0 |        1.936 |        0.109 |     0.200 |      0.691 |
| dino_neg                     | multiple |       18 |        0 |        1.222 |        0.222 |     0.444 |      0.333 |
| dino_neg                     | one      |      272 |        0 |        0.599 |        0.401 |     0.599 |      0.000 |
| dino_neg                     | zero     |      110 |        0 |        0.127 |        0.873 |     0.127 |      0.000 |
| owlv2                        | multiple |       18 |        0 |        2.833 |        0.000 |     0.333 |      0.667 |
| owlv2                        | one      |      272 |        0 |        1.136 |        0.033 |     0.827 |      0.140 |
| owlv2                        | zero     |      110 |        0 |        0.518 |        0.545 |     0.409 |      0.045 |
| owlv2_neg                    | multiple |       18 |        0 |        2.833 |        0.000 |     0.333 |      0.667 |
| owlv2_neg                    | one      |      272 |        0 |        1.051 |        0.077 |     0.816 |      0.107 |
| owlv2_neg                    | zero     |      110 |        0 |        0.100 |        0.909 |     0.082 |      0.009 |
| qwen3vl                      | multiple |       18 |        0 |        3.833 |        0.000 |     0.278 |      0.722 |
| qwen3vl                      | one      |      272 |        0 |        1.004 |        0.000 |     0.996 |      0.004 |
| qwen3vl                      | zero     |      110 |        0 |        0.373 |        0.655 |     0.318 |      0.027 |
| qwen3vl__nms_0.9             | multiple |       18 |        0 |        2.889 |        0.000 |     0.278 |      0.722 |
| qwen3vl__nms_0.9             | one      |      272 |        0 |        1.004 |        0.000 |     0.996 |      0.004 |
| qwen3vl__nms_0.9             | zero     |      110 |        0 |        0.373 |        0.655 |     0.318 |      0.027 |
| qwen3vl_neg                  | multiple |       18 |        0 |        5.056 |        0.000 |     0.111 |      0.889 |
| qwen3vl_neg                  | one      |      272 |        0 |        1.011 |        0.000 |     0.989 |      0.011 |
| qwen3vl_neg                  | zero     |      110 |        0 |        0.327 |        0.936 |     0.045 |      0.018 |
| qwen3vl_neg__nms_0.9         | multiple |       18 |        0 |        3.778 |        0.000 |     0.111 |      0.889 |
| qwen3vl_neg__nms_0.9         | one      |      272 |        0 |        1.007 |        0.000 |     0.993 |      0.007 |
| qwen3vl_neg__nms_0.9         | zero     |      110 |        0 |        0.127 |        0.936 |     0.045 |      0.018 |

Photos without butterflies (count = zero) by negative_kind:

| run                          | negative_kind   |   photos |   with_box |   mean_boxes |
|:-----------------------------|:----------------|---------:|-----------:|-------------:|
| dino_butterfly               | immature        |       19 |      1.000 |        1.158 |
| dino_butterfly               | ordinary        |       54 |      0.889 |        1.759 |
| dino_butterfly               | other_insect    |       35 |      1.000 |        1.400 |
| dino_butterfly               | other_similar   |        2 |      1.000 |        1.500 |
| dino_butterfly_moth          | immature        |       19 |      1.000 |        1.053 |
| dino_butterfly_moth          | ordinary        |       54 |      0.778 |        1.148 |
| dino_butterfly_moth          | other_insect    |       35 |      1.000 |        1.314 |
| dino_butterfly_moth          | other_similar   |        2 |      1.000 |        2.500 |
| dino_butterfly_moth__nms_off | immature        |       19 |      1.000 |        2.263 |
| dino_butterfly_moth__nms_off | ordinary        |       54 |      0.778 |        1.444 |
| dino_butterfly_moth__nms_off | other_insect    |       35 |      1.000 |        2.486 |
| dino_butterfly_moth__nms_off | other_similar   |        2 |      1.000 |        2.500 |
| dino_neg                     | immature        |       19 |      0.053 |        0.053 |
| dino_neg                     | ordinary        |       54 |      0.056 |        0.056 |
| dino_neg                     | other_insect    |       35 |      0.286 |        0.286 |
| dino_neg                     | other_similar   |        2 |      0.000 |        0.000 |
| owlv2                        | immature        |       19 |      0.842 |        0.895 |
| owlv2                        | ordinary        |       54 |      0.111 |        0.148 |
| owlv2                        | other_insect    |       35 |      0.800 |        0.914 |
| owlv2                        | other_similar   |        2 |      0.000 |        0.000 |
| owlv2_neg                    | immature        |       19 |      0.053 |        0.053 |
| owlv2_neg                    | ordinary        |       54 |      0.111 |        0.130 |
| owlv2_neg                    | other_insect    |       35 |      0.086 |        0.086 |
| owlv2_neg                    | other_similar   |        2 |      0.000 |        0.000 |
| qwen3vl                      | immature        |       19 |      0.105 |        0.105 |
| qwen3vl                      | ordinary        |       54 |      0.056 |        0.056 |
| qwen3vl                      | other_insect    |       35 |      0.943 |        1.029 |
| qwen3vl                      | other_similar   |        2 |      0.000 |        0.000 |
| qwen3vl__nms_0.9             | immature        |       19 |      0.105 |        0.105 |
| qwen3vl__nms_0.9             | ordinary        |       54 |      0.056 |        0.056 |
| qwen3vl__nms_0.9             | other_insect    |       35 |      0.943 |        1.029 |
| qwen3vl__nms_0.9             | other_similar   |        2 |      0.000 |        0.000 |
| qwen3vl_neg                  | immature        |       19 |      0.000 |        0.000 |
| qwen3vl_neg                  | ordinary        |       54 |      0.093 |        0.630 |
| qwen3vl_neg                  | other_insect    |       35 |      0.057 |        0.057 |
| qwen3vl_neg                  | other_similar   |        2 |      0.000 |        0.000 |
| qwen3vl_neg__nms_0.9         | immature        |       19 |      0.000 |        0.000 |
| qwen3vl_neg__nms_0.9         | ordinary        |       54 |      0.093 |        0.222 |
| qwen3vl_neg__nms_0.9         | other_insect    |       35 |      0.057 |        0.057 |
| qwen3vl_neg__nms_0.9         | other_similar   |        2 |      0.000 |        0.000 |
