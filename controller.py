from xml.dom.pulldom import END_ELEMENT
from crypt import methods
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import Flask, render_template
from sr.sr_algos import *
from sr_kaldi.speech import *
from audio.vlc import *
from visualizations.graphs import *
from rtvc.demo_cli import *
import matplotlib.pyplot as plt
from pandas.plotting import table

confidence = []
audio_trait_file = ""
predicted_text = ""
other_predictions = []
word = ""
time = ""

app = Flask(__name__)
upload_folder = os.path.join('static', 'upload')
images_folder = os.path.join('static', 'visualizations')
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['IMAGE_FOLDER'] = images_folder

@app.route('/statistics', methods=['GET', 'POST'])
def statistics():
    global confidence
    global audio_trait_file
    global other_predictions
    global predicted_text
    global word
    global time
    if request.method == 'POST':
          editted = request.form.get('text')
          # editted = "one zero zero zero one nah no to i know zero one zero three"
          # # editted = "one zero zero zero one nine six no to i know zero one saif zero three"

          print("LOG: Getting cuts of edits")
          changes_dict = get_changes_start_end(predicted_text, editted, confidence)
          
          print(changes_dict)
          
          print("LOG: Exporting final audio")
          export_final(changes_dict, audio_trait_file)
          
          word = list(changes_dict.keys())[0]
          time = changes_dict[list(changes_dict.keys())[0]][0]
          
          print("LOG: File exported at speech/final.wav")
          
          plot1 = os.path.join(app.config['IMAGE_FOLDER'], 'catplot0.png')
          plot2 = os.path.join(app.config['IMAGE_FOLDER'], 'catplot1.png')
          timetable = os.path.join(app.config['IMAGE_FOLDER'], 'timetable.png')
          
    return render_template('statistics.html', plot1=plot1, plot2=plot2, timetable=timetable, other_predictions=other_predictions, confidence=confidence, word=word, time=time)

@app.route('/deepvoice', methods=['GET', 'POST'])
def deepvoice():
    global word
    global time
    return render_template('audio.html', word=word, time=time)

@app.route('/text', methods=['GET', 'POST'])
def text():
    global confidence
    global audio_trait_file
    global predicted_text
    global other_predictions
    if request.method == 'POST':
        f = request.files['file']
        if f:
            filename = secure_filename(f.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'],filename)
            f.save(filepath)
            print("\n[LOG]: Uploaded file " + filename + " to " + app.config['UPLOAD_FOLDER'] + "\n")
            audio_trait_file = filepath
            
            # working with other sr algorithms
            text, confidence = google(audio_trait_file)
            other_predictions.append((text, confidence))
            text, confidence = houndify(audio_trait_file)
            other_predictions.append((text, confidence))
            text, confidence = wit(audio_trait_file)
            other_predictions.append((text, confidence))
            text, confidence = ibm(audio_trait_file)
            other_predictions.append((text, confidence))

            # # # working with kaldi
            print("LOG: Starting Kaldi")
            model = sr_model(audio_trait_file)    
            variants = model.get_var_conf()
            print("LOG: Results from Kaldi")
            text, confidence = model.get_conf_end_start_word()
            predicted_text = text
            
            print("LOG: Plots from Kaldi")
            # plot_all(variants, count=2)
            
    return render_template('text.html', text=text)

@app.route('/')
def index():
    return render_template('index.html')
  
def get_changes_start_end(text, edits, confidence):
  original = text.split()
  editted = edits.split()
  
  # find the indexes of words that are changed in the original and editted
  # case 1: added words
  # case 2: deleted words
  # case 3: changed words
  start = -1
  end = -1
  orig_index = 0
  edit_index = 0
  del_count = 0
  altered_text = []
  dict = {}
  while(edit_index < len(editted)):
    if(editted[edit_index] == original[orig_index]):
      orig_index += 1
      
      if(start != -1 and end != -1):
        key = ' '.join(altered_text)
        dict[key if len(key) != 0 else del_count] = (start, end)
        if len(key) == 0:
          del_count += 1
        altered_text = []
        start = -1
        end = -1
      
    elif (editted[edit_index] in original[orig_index:]):
      found_at = orig_index + original[orig_index:].index(editted[edit_index])
      start = confidence[orig_index]['start']
      end = confidence[found_at]['start']
      orig_index = found_at + 1
    else:
      start = confidence[orig_index]['start']
      altered_text.append(editted[edit_index])
      
      while(True):
        edit_index += 1
        if(edit_index < len(editted)):
          if(editted[edit_index] in original[orig_index:]):
            found_at = orig_index + original[orig_index:].index(editted[edit_index])
            end = confidence[found_at]['start']
            orig_index += 1
            break
          else:
            orig_index += 1
            altered_text.append(editted[edit_index])
        else:
          end = -1
          break
    edit_index += 1
    
  if(start != -1 and end != -1):
    key = ' '.join(altered_text)
    dict[key if len(key) != 0 else del_count] = (start, end)
    if len(key) == 0:
      del_count += 1
    altered_text = []
    start = -1
    end = -1
  
  # if both are same means, altered_text is added at the start/end
  # if start < end but altered_text is empty, it means, something is deleted
  # if start < end but altered_text is not empty, it means, something is changed
  # if start > 0 and end = -1, means something is changed/added at the end
  return dict

def export_final(changes_dict, audio_trait_file):
  for i in changes_dict.keys():
    file_count = list(changes_dict.keys()).index(i)
    altered_text = i
    # text empty, meaning delete
    if(type(i) == int):
      main_audio = audio(audio_trait_file)
      start = ':'.join(str(changes_dict[i][0]).split('.'))
      end = ':'.join(str(changes_dict[i][1]).split('.'))
      actual_end = ':'.join(str(main_audio.len()).split('.'))
      main_audio.trim_and_attach("0:0", start, end, actual_end)
      main_audio.export(os.path.join(app.config['UPLOAD_FOLDER'],"final.wav"))
    
    elif(changes_dict[i][0] == changes_dict[i][1]):
      # making the deep voice
      destination_file = (os.path.join(app.config['UPLOAD_FOLDER'],"chunk"+str(file_count)+".wav"))
      rtvc(audio_trait_file, altered_text, destination_file)
      
      # text not empty, and both same meaning add
      start = ':'.join(str(changes_dict[i][0]).split('.'))
      
      altered_chunk = audio(destination_file)
      main_audio = audio(audio_trait_file)
      main_audio.add_between(altered_chunk, start)
      main_audio.export(os.path.join(app.config['UPLOAD_FOLDER'],"final.wav"))
      
    else:
      # making the deep voice
      destination_file = (os.path.join(app.config['UPLOAD_FOLDER'],"chunk"+str(file_count)+".wav"))
      rtvc(audio_trait_file, altered_text, destination_file)
      
      # text not empty, and both different meaning update
      start = ':'.join(str(changes_dict[i][0]).split('.'))
      end = ':'.join(str(changes_dict[i][1]).split('.'))
      
      altered_chunk = audio(destination_file)
      main_audio = audio(audio_trait_file)
      main_audio.change_between(altered_chunk, start, end)
      main_audio.export(os.path.join(app.config['UPLOAD_FOLDER'],"final.wav"))

if __name__ == "__main__":
  app.run(debug=True)