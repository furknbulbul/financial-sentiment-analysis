import numpy as np
import torch
from torch import nn

from transformers import BertModel

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


# 1. pretrained model  = bert base uncased
# 2. pretreained model = finbert

class SentimentClassifier(nn.Module):

    def __init__(self, n_classes, pre_train_model, model_name="bert-base", do_fine_tune=False):
        super(SentimentClassifier, self).__init__()
        self.bert = BertModel.from_pretrained(pre_train_model, return_dict=False)
        self.do_fine_tune = do_fine_tune
        self.model_name = model_name
        if do_fine_tune:
            self.drop = nn.Dropout(p=0.3)  # dropout layer
            self.model_name = model_name 
        self.out = nn.Linear(self.bert.config.hidden_size, n_classes)  # output layer with nodes of number of classes

    def forward(self, input_ids, attention_mask):

        _, pooled_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        if self.do_fine_tune:
            output = self.drop(pooled_output)
        else:
            output = pooled_output
        return self.out(output)

