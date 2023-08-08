from transformers import BertTokenizer
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import DataCollatorWithPadding

RANDOM_SEED = 42
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class NewsDataset(Dataset):
    def __init__(self, news, labels, tokenizer, max_len, include_raw_text=False):
        self.news = news
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.include_raw_text = include_raw_text

    # __len__ so that len(dataset) returns the size of the dataset.
    def __len__(self):
        return len(self.news)

    # __getitem__ to support the indexing such that dataset[i] can be used to get i th sample.
    def __getitem__(self, item):
        new = str(self.news[item])
        label = self.labels[item]
        encoding = self.tokenizer.encode_plus(
            new,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            return_attention_mask=True,
            truncation=True,
            padding=True,
            return_tensors='pt')

        """
        input_ids: Lists of token IDs that represent the input text. The integers correspond to the tokens in the tokenizer's vocabulary.
        attention_mask: Lists of binary values that indicate whether a given token should be attended to (1) or not (0).
        """

        output = {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

        return output


# pre_train_model = 'bert-base-uncased'
# tokenizer = BertTokenizer.from_pretrained(pre_train_model)
# collator = DataCollatorWithPadding(tokenizer=tokenizer, padding='max_length')


# before convert df to appropriate format, we need to split the data into train and test
def create_data_loader(df, tokenizer, max_len, batch_size, include_raw_text=False):
    collator = DataCollatorWithPadding(tokenizer=tokenizer, padding='max_length')
    ds = NewsDataset(
        news=df.news.to_list(),
        labels=df.labels.to_list(),
        tokenizer=tokenizer,
        max_len=max_len,
        include_raw_text=include_raw_text
    )
    return DataLoader(ds, batch_size=batch_size, collate_fn=collator)
