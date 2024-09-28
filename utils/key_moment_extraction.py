# utils/key_moment_extraction.py

import logging
import numpy as np
from sklearn.cluster import DBSCAN
from transformers import AutoTokenizer, AutoModel
import torch
from scipy.signal import find_peaks
from copy import deepcopy

def extract_key_moments_advanced(transcription, num_clips=4, clip_len=15, labels= ['человек', 'спорт', 'машины'], model=None, tokenizer=None, words=None):
    labels_features = []
    for segment in labels:
        inputs = tokenizer(segment, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs).pooler_output
        labels_features.append(outputs)
    labels_features = torch.cat(labels_features, dim=0)

    text_features = []

    for segment in transcription:
        inputs = tokenizer(segment['text'], return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs).pooler_output
        text_features.append(outputs)
    text_features = torch.cat(text_features, dim=0)
    labels_features = labels_features / labels_features.norm(dim=1, keepdim=True)
    text_features = text_features / text_features.norm(dim=1, keepdim=True)
    logits = text_features @ labels_features.t()
    logits_list = list(logits.sum(dim=-1).numpy())
    logits_idx = sorted([[logits_list[i], i] for i in range(len(logits_list))])[::-1][:num_clips]
    clips = []
    for clip in logits_idx:
        i_clip = clip[1]
        start = transcription[i_clip]['start']
        end = transcription[i_clip]['end']
        text = transcription[i_clip]['text']
        left = True
        left_ind = i_clip
        right_ind = i_clip
        while True:
            if end - start >= clip_len or (right_ind + 1 == len(transcription) and left_ind == 0):
                clips.append({'start': start, 'end': end, 'text': text})
                break
            if left and left_ind != 0:
                left = False
                left_ind -= 1
                start = transcription[left_ind]['start']
                text = transcription[left_ind]['text'] + ' ' + text
            elif right_ind + 1 != len(transcription):
                left = True
                right_ind += 1
                end = transcription[right_ind]['end']
                text = text + ' ' + transcription[right_ind]['text']
                pass
    words_for_clips = []
    if words is not None:
        for clip in clips:
            words_for_clip = []
            for word in words:
                if  word['start'] >= clip['start']:
                    word_new = deepcopy(word)
                    word_new['start'] -= clip['start']
                    words_for_clip.append(word_new)
                if word['end'] >= clip['end']:
                    break
            words_for_clips.append(words_for_clip)
    return clips, words_for_clips
