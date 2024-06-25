<template>
  <div class="code-visualization-wrapper">
    <div class="controls-wrapper">
      <el-select v-model="selectedFile" placeholder="Select JSON File" @change="loadData">
        <el-option v-for="file in files" :key="file" :label="file" :value="file"></el-option>
      </el-select>
    </div>
    <div class="controls-wrapper">
      <el-select v-model="selectedFileCompare" placeholder="Select JSON File" @change="loadDataCompare">
        <el-option v-for="file in files" :key="file" :label="file" :value="file"></el-option>
      </el-select>
    </div>
    <div class="controls-wrapper">
      <el-checkbox v-model="useCompare">Use Compare Data</el-checkbox>
    </div>
        <div class="controls-wrapper">
      <el-checkbox v-model="useRank">Use Rank</el-checkbox>
    </div>
    <div class="buttons-wrapper">
      <el-button type="primary" @click="readingFirst">Reading First</el-button>
      <el-button type="primary" @click="readingLast">Reading Last</el-button>
      <el-button type="primary" @click="readingAll">Reading All</el-button>
      <el-button type="primary" @click="codingFirst">Coding First</el-button>
      <el-button type="primary" @click="codingLast">Coding Last</el-button>
      <el-button type="primary" @click="codingAll">Coding All</el-button>
    </div>
    <div class="extra-code-display">
      <pre class="code-block">{{ currentFix }}</pre>
    </div>
    <div class="extra-code-display">
      <pre class="code-block">{{ code }}</pre>
    </div>
    <CodeVisualization
      :key="getKey(selectedFile, selectedFileCompare, type)"
      :code="currentCode"
      :attentionData="currentAttentionData"
      style="margin-top: 20px"
    />
  </div>
</template>
<!--    <Diff-->
<!--            mode="split"-->
<!--            theme="light"-->
<!--            language="text"-->
<!--            :prev="buggy"-->
<!--            :current="oracle"-->
<!--            style="width: 100%; overflow: scroll"-->
<!--    />-->
<script>
import CodeVisualization from "@/components/CodeVisualization.vue";

export default {
  name: "CodeView",
  components: {
    CodeVisualization,
  },
  data() {
    return {
      files: [],
      selectedFile: '',
      code: "",
      attentionData: [],
      attentions: {},
      type: "",
      oracle: "",
      buggy: "",
      fix: "",
      selectedFileCompare: "",
      codeCompare: "",
      attentionsCompare: {},
      useCompare: false,
      raw_attentions: [],
      viewcode: "",
      rank_raw_attentions: [],
      useRank: false
    };
  },
  mounted() {
    this.loadFiles();
  },
  methods: {
    loadFiles() {
      fetch('/api/list')
        .then(response => response.json())
        .then(data => {
          this.files = data;
        })
        .catch(error => {
          console.error('Error fetching JSON file list:', error);
        });
    },
    loadDataCompare() {
      if (!this.selectedFileCompare) return;
      const parseData = (res) => {
        const normalize = (value, min, max, on) => {
          if (on) return (value - min) / (max - min);
          return value;
        };

        const transformList = (list) => {
          const attentionValues = list.map(item => item[2]);
          const minAttention = Math.min(...attentionValues);
          const maxAttention = Math.max(...attentionValues);

          return list.map(item => ({
            range: item[3],
            attention: normalize(item[2], minAttention, maxAttention, true)
          }));
        };

        return {
          readingFirst: transformList(res.reading_first),
          readingLast: transformList(res.reading_last),
          readingAll: transformList(res.reading_all),
          codingFirst: transformList(res.coding_first),
          codingLast: transformList(res.coding_last),
          codingAll: transformList(res.coding_all)
        };
      };

      fetch(`/api/data/${this.selectedFileCompare}`)
        .then(response => response.json())
        .then(data => {
          // if(!("coding_all" in data.res)) {
          //
          // }
          this.codeCompare = data.prompt;
          this.attentionsCompare = {
            'codingAll': [],
            'codingFirst': [],
            'codingLast': [],
            'readingAll': [],
            'readingFirst': [],
            'readingLast': []
          };
          const lengthToCompare = Math.min(this.raw_attentions.reading_all.length, data.res.reading_all.length);
          const rank = (res) => {
              const rankLogic = (list) => {
                  // Step 1: Extract Attention values
                  const attentionValues = list.map(subList => subList[2]);

                  // Step 2: Sort Attention values
                  const sortedAttentionValues = [...attentionValues].sort((a, b) => a - b);

                  // Step 3: Append rank to each subList
                  return list.map(subList => {
                      const attention = subList[2];
                      const rank = sortedAttentionValues.indexOf(attention) + 1;
                      return [...subList, rank];
                  });
              };
              const safeRankLogic = (list) => list ? rankLogic(list) : [];
              return {
                  reading_first: safeRankLogic(res.reading_first),
                  reading_last: safeRankLogic(res.reading_last),
                  reading_all: safeRankLogic(res.reading_all),
                  coding_first: safeRankLogic(res.coding_first),
                  coding_last: safeRankLogic(res.coding_last),
                  coding_all: safeRankLogic(res.coding_all)
              }
          }
          console.log(this.rank_raw_attentions)
          const res = rank(data.res)
          if(this.useRank) {
              for (let i = 0; i < lengthToCompare; i++) {
                  if (this.raw_attentions.reading_all[i][1] !== data.res.reading_all[i][1]) {
                      break;
                  }

                  if ("coding_all" in data.res) {
                      this.attentionsCompare.codingAll.push({
                          range: this.rank_raw_attentions.coding_all[i][3],
                          attention: (this.rank_raw_attentions.coding_all[i][4] - res.coding_all[i][4])/200
                      });
                  }

                  if ("coding_first" in data.res) {
                      this.attentionsCompare.codingFirst.push({
                          range: this.rank_raw_attentions.coding_first[i][3],
                          attention: (this.rank_raw_attentions.coding_first[i][4] - res.coding_first[i][4])/200
                      });
                  }

                  if ("coding_first" in data.res) {
                      this.attentionsCompare.codingLast.push({
                          range: this.rank_raw_attentions.coding_last[i][3],
                          attention: (this.rank_raw_attentions.coding_last[i][4] - res.coding_last[i][4])/200
                      });
                  }

                  this.attentionsCompare.readingAll.push({
                      range: this.rank_raw_attentions.reading_all[i][3],
                      attention: (this.rank_raw_attentions.reading_all[i][4] - res.reading_all[i][4])/200
                  });

                  this.attentionsCompare.readingFirst.push({
                      range: this.rank_raw_attentions.reading_first[i][3],
                      attention: (this.rank_raw_attentions.reading_first[i][4] - res.reading_first[i][4])/200
                  });

                  this.attentionsCompare.readingLast.push({
                      range: this.rank_raw_attentions.reading_last[i][3],
                      attention: (this.rank_raw_attentions.reading_last[i][4] - res.reading_last[i][4])/200
                  });
              }
          }else {
              for (let i = 0; i < lengthToCompare; i++) {
                  if (this.raw_attentions.reading_all[i][1] !== data.res.reading_all[i][1]) {
                      break;
                  }

                  if ("coding_all" in data.res) {
                      this.attentionsCompare.codingAll.push({
                          range: this.raw_attentions.coding_all[i][3],
                          attention: this.raw_attentions.coding_all[i][2] - data.res.coding_all[i][2]
                      });
                  }

                  if ("coding_first" in data.res) {
                      this.attentionsCompare.codingFirst.push({
                          range: this.raw_attentions.coding_first[i][3],
                          attention: this.raw_attentions.coding_first[i][2] - data.res.coding_first[i][2]
                      });
                  }

                  if ("coding_first" in data.res) {
                      this.attentionsCompare.codingLast.push({
                          range: this.raw_attentions.coding_last[i][3],
                          attention: this.raw_attentions.coding_last[i][2] - data.res.coding_last[i][2]
                      });
                  }

                  this.attentionsCompare.readingAll.push({
                      range: this.raw_attentions.reading_all[i][3],
                      attention: this.raw_attentions.reading_all[i][2] - data.res.reading_all[i][2]
                  });

                  this.attentionsCompare.readingFirst.push({
                      range: this.raw_attentions.reading_first[i][3],
                      attention: this.raw_attentions.reading_first[i][2] - data.res.reading_first[i][2]
                  });

                  this.attentionsCompare.readingLast.push({
                      range: this.raw_attentions.reading_last[i][3],
                      attention: this.raw_attentions.reading_last[i][2] - data.res.reading_last[i][2]
                  });
              }
          }
        })
        .catch(error => {
          console.error('Error fetching JSON data:', error);
        });
    },
    loadData() {
      if (!this.selectedFile) return;

      const parseData = (res) => {
        const normalize = (value, min, max, on) => {
          if (on) return (value - min) / (max - min);
          return value;
        };
        function sum(arr){
          return arr.reduce((prev,cur)=> prev+cur)
        }
        const transformList = (list) => {
          const attentionValues = list.map(item => item[2]);
          const minAttention = Math.min(...attentionValues);
          const maxAttention = Math.max(...attentionValues);

          return list.map(item => ({
            range: item[3],
            attention: normalize(item[2], minAttention, maxAttention, true)
          }));
        };

        const safeTransformList = (list) => list ? transformList(list) : [];

        return {
          readingFirst: safeTransformList(res.reading_first),
          readingLast: safeTransformList(res.reading_last),
          readingAll: safeTransformList(res.reading_all),
          codingFirst: safeTransformList(res.coding_first),
          codingLast: safeTransformList(res.coding_last),
          codingAll: safeTransformList(res.coding_all)
        };
      };
      const rank = (res) => {
          const rankLogic = (list) => {
              // Step 1: Extract Attention values
              const attentionValues = list.map(subList => subList[2]);

              // Step 2: Sort Attention values
              const sortedAttentionValues = [...attentionValues].sort((a, b) => a - b);

              // Step 3: Append rank to each subList
              return list.map(subList => {
                  const attention = subList[2];
                  const rank = sortedAttentionValues.indexOf(attention) + 1;
                  return [...subList, rank];
              });
          };
          const safeRankLogic = (list) => list ? rankLogic(list) : [];
          return {
              reading_first: safeRankLogic(res.reading_first),
              reading_last: safeRankLogic(res.reading_last),
              reading_all: safeRankLogic(res.reading_all),
              coding_first: safeRankLogic(res.coding_first),
              coding_last: safeRankLogic(res.coding_last),
              coding_all: safeRankLogic(res.coding_all)
          }
      }
      fetch(`/api/data/${this.selectedFile}`)
        .then(response => response.json())
        .then(data => {
          this.code = data.prompt;
          this.attentions = parseData(data.res);
          this.raw_attentions = data.res;
          this.rank_raw_attentions = rank(data.res);
          this.fix = data.fix;
          this.oracle = data.data.solution;
          this.buggy = data.data.buggy_code;
        })
        .catch(error => {
          console.error('Error fetching JSON data:', error);
        });
      this.loadDataCompare()
    },
    readingFirst() {
      this.type = "readingFirst";
      this.attentionData = this.useCompare
        ? this.attentionsCompare.readingFirst || []
        : this.attentions.readingFirst || [];
    },
    codingFirst() {
      this.type = "codingFirst";
      this.attentionData = this.useCompare
        ? this.attentionsCompare.codingFirst || []
        : this.attentions.codingFirst || [];
    },
    readingLast() {
      this.type = "readingLast";
      this.attentionData = this.useCompare
        ? this.attentionsCompare.readingLast || []
        : this.attentions.readingLast || [];
    },
    codingLast() {
      this.type = "codingLast";
      this.attentionData = this.useCompare
        ? this.attentionsCompare.codingLast || []
        : this.attentions.codingLast || [];
    },
    readingAll() {
      this.type = "readingAll";
      this.attentionData = this.useCompare
        ? this.attentionsCompare.readingAll || []
        : this.attentions.readingAll || [];
    },
    codingAll() {
      this.type = "codingAll";
      this.attentionData = this.useCompare
        ? this.attentionsCompare.codingAll || []
        : this.attentions.codingAll || [];
      console.log(this.attentionData)
    },
    getKey(selectedFile, selectedFileCompare, type) {
      return `${selectedFile}-${selectedFileCompare}-${type}`;
    },
    diffAttention(attention1, attention2) {

    }
  },
  computed: {
    currentCode() {
      return this.useCompare ? this.codeCompare : this.code;
    },
    currentAttentionData() {
      return this.attentionData;
    },
    currentFix() {
      return this.fix;
    },
  },
};
</script>

<style scoped>
.code-visualization-wrapper {
  justify-content: center;
  align-items: center;
}

.controls-wrapper {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.buttons-wrapper {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.code-block {
  text-align: left;
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 5px;
  background-color: #f9f9f9;
  white-space: pre-wrap;
  font-family: monospace;
}
</style>
