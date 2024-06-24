<template>
    <div>
        <el-button type="primary" @click="autoScale" style="margin-bottom: 10px">Autoscale</el-button>
        Scale: <input type="number" v-model.number="scale" @input="renderCode" style="width: 60px; margin-right: 10px;" />
        <span>{{ scale }}</span>
        <el-switch v-model="useSteps" active-text="Use Steps" inactive-text="Use Continuous" style="margin-bottom: 10px;"></el-switch>
        <div class="code-visualization-container">
            <input type="range" min="1" max="100" v-model="scale" @input="renderCode" />
            <pre id="code-container" ref="codeContainer"></pre>
            <div class="tooltip" ref="tooltip"></div>
        </div>
    </div>
</template>

<script>
import * as d3 from "d3";

export default {
    name: "CodeVisualization",
    props: {
        code: {
            type: String,
            required: true
        },
        attentionData: {
            type: Array,
            required: true
        }
    },
    data() {
        return {
            scale: 1,
            useSteps: false
        };
    },
    mounted() {
        this.renderCode();
    },
    methods: {
        autoScale() {
            let maxAttention = -1;
            this.attentionData.forEach((segment) => {
                if (Math.abs(segment.attention) > 0 && Math.abs(segment.attention) > maxAttention) {
                    maxAttention = Math.abs(segment.attention);
                }
            });
            this.scale = 32 / maxAttention;
            this.renderCode();
        },
        generateFullAttentionData() {
            const fullData = [];
            let currentPos = 0;
            this.attentionData.forEach((segment) => {
                if (segment.range[0] > currentPos) {
                    fullData.push({
                        range: [currentPos, segment.range[0]],
                        attention: 0,
                    });
                }
                fullData.push(segment);
                currentPos = segment.range[1];
            });
            if (currentPos < this.code.length) {
                fullData.push({
                    range: [currentPos, this.code.length],
                    attention: 0,
                });
            }
            return fullData;
        },
        renderCode() {
            const container = d3.select(this.$refs.codeContainer);
            const tooltip = d3.select(this.$refs.tooltip);

            // Clear the container before rendering
            container.html("");

            const fullAttentionData = this.generateFullAttentionData();

            if (this.useSteps) {
                // 按 attention 值排序 token 数据
                const sortedTokens = this.attentionData.slice().sort((a, b) => - Math.abs(b.attention) + Math.abs(a.attention));
                const stepSize = 10; // 每个阶梯的大小
                const stepColors = d3.scaleSequential(d3.interpolateBlues).domain([0, Math.ceil(sortedTokens.length / stepSize)]);

                // 渲染 token 数据
                fullAttentionData.forEach(segment => {
                    let color = "";
                    for (let i = 0; i < sortedTokens.length; i += stepSize) {
                        if (sortedTokens.slice(i, i + stepSize).includes(segment)) {
                            color = stepColors(Math.floor(i / stepSize));
                            break;
                        }
                    }

                    // 将token按原始代码排版
                    const token = this.code.slice(segment.range[0], segment.range[1]);
                    const lines = token.split("\n");
                    lines.forEach((line, lineIndex) => {
                        if (lineIndex > 0) {
                            container.append("div").attr("class", "code-line");
                        }
                        container.append("span")
                            .attr("class", "code-char")
                            .style("background-color", color)
                            .text(line)
                            .on("mouseover", (event) => {
                                tooltip
                                    .style("visibility", "visible")
                                    .text(`Attention: ${segment.attention}`)
                                    .style("top", event.pageY + 10 + "px")
                                    .style("left", event.pageX + 10 + "px");
                            })
                            .on("mousemove", (event) => {
                                tooltip
                                    .style("top", event.pageY + 10 + "px")
                                    .style("left", event.pageX + 10 + "px");
                            })
                            .on("mouseout", () => {
                                tooltip.style("visibility", "hidden");
                            });
                    });
                });
            } else {
                // 渲染 token 数据，保持原有格式
                fullAttentionData.forEach(segment => {
                    const color = segment.attention >= 0
                        ? d3.interpolateBlues(segment.attention * this.scale)
                        : d3.interpolateReds(-segment.attention * this.scale);

                    // 将token按原始代码排版
                    const token = this.code.slice(segment.range[0], segment.range[1]);
                    const lines = token.split("\n");
                    lines.forEach((line, lineIndex) => {
                        if (lineIndex > 0) {
                            container.append("div").attr("class", "code-line");
                        }
                        container.append("span")
                            .attr("class", "code-char")
                            .style("background-color", color)
                            .text(line)
                            .on("mouseover", (event) => {
                                tooltip
                                    .style("visibility", "visible")
                                    .text(`Attention: ${segment.attention}`)
                                    .style("top", event.pageY + 10 + "px")
                                    .style("left", event.pageX + 10 + "px");
                            })
                            .on("mousemove", (event) => {
                                tooltip
                                    .style("top", event.pageY + 10 + "px")
                                    .style("left", event.pageX + 10 + "px");
                            })
                            .on("mouseout", () => {
                                tooltip.style("visibility", "hidden");
                            });
                    });
                });
            }
        },
    },
};
</script>

<style>
.code-visualization-container {
    border: 1px solid #ccc;
    padding: 10px;
    border-radius: 5px;
}

#code-container {
    font-family: monospace;
    white-space: pre;
    text-align: left;
}

.code-line {
    display: block;
    text-align: left;
}

.code-char {
    display: inline-block;
    padding: 0 1px;
    border-radius: 2px;
}

.tooltip {
    position: absolute;
    text-align: center;
    padding: 5px;
    background: lightsteelblue;
    border: 0px;
    border-radius: 8px;
    pointer-events: none;
    visibility: hidden;
}

input[type="range"] {
    width: 100%;
    margin-bottom: 10px;
}
</style>