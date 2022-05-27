import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

class visualizer():
    def __init__(self, data, cols, kind="catplot"):
        if(type(data) != pd.core.frame.DataFrame):
            self.data = pd.DataFrame(data, columns=cols)
        else:
            self.data = data
        self.kind = kind
    
    def plot(self, against):
        if(self.kind == "catplot"):
            sns.catplot(x="confidence", y="text", kind="bar", data=self.data)
            max = self.data.max(axis=0)['confidence']
            min = self.data.min(axis=0)['confidence']
            plt.xlim(min-(max-min), max)
        
    def save(self, path):
        plt.savefig(path)
        print("Saved at: ", path)

def plot_all(variants, count = 2):
    print()
    image_count = 0
    print("plotting catplot of conf vs text:")
    data = []
    for i in variants:
        data.append([i[0]['confidence'],i[0]['text']])
    vis = visualizer(data, ['confidence', 'text'], "catplot")
    vis.plot("confidence")
    vis.save('static/visualizations/catplot'+str(image_count)+'.png')
    
    image_count += 1
    print()
    print("Plotting catplot of conf vs variants:")
    data = []
    for sentence_variants in variants:
        if(len(sentence_variants) > 1):
            for variant in sentence_variants:
                data.append([variant['confidence'], variant['text']])
    
    vis = visualizer(data, ['confidence', 'text'], "catplot")
    vis.plot("confidence")
    vis.save('static/visualizations/catplot'+str(image_count)+'.png')
    print()
    