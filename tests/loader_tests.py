import os
import unittest
import numpy as np
import torch

from torch.utils.data import DataLoader
from torch.autograd import Variable
from TTS.utils.generic_utils import load_config
from TTS.datasets.LJSpeech import LJSpeechDataset
from TTS.datasets.TWEB import TWEBDataset
from TTS.datasets.utils import TBPTT


file_path = os.path.dirname(os.path.realpath(__file__))
c = load_config(os.path.join(file_path, 'test_config.json'))


class TestLJSpeechDataset(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestLJSpeechDataset, self).__init__(*args, **kwargs)
        self.max_loader_iter = 4

    def test_loader(self):
        dataset = LJSpeechDataset(os.path.join(c.data_path_LJSpeech, 'metadata.csv'),
                                  os.path.join(c.data_path_LJSpeech, 'wavs'),
                                  c.r,
                                  c.sample_rate,
                                  c.text_cleaner,
                                  c.num_mels,
                                  c.min_level_db,
                                  c.frame_shift_ms,
                                  c.frame_length_ms,
                                  c.preemphasis,
                                  c.ref_level_db,
                                  c.num_freq,
                                  c.power
                                  )

        dataloader = DataLoader(dataset, batch_size=2,
                                shuffle=True, collate_fn=dataset.collate_fn,
                                drop_last=True, num_workers=c.num_loader_workers)

        for i, data in enumerate(dataloader):
            if i == self.max_loader_iter:
                break
            text_input = data[0]
            text_lengths = data[1]
            linear_input = data[2]
            mel_input = data[3]
            mel_lengths = data[4]
            stop_target = data[5]
            item_idx = data[6]

            neg_values = text_input[text_input < 0]
            check_count = len(neg_values)
            assert check_count == 0, \
                " !! Negative values in text_input: {}".format(check_count)
            # TODO: more assertion here
            assert linear_input.shape[0] == c.batch_size
            assert mel_input.shape[0] == c.batch_size
            assert mel_input.shape[2] == c.num_mels

    def test_padding(self):
        dataset = LJSpeechDataset(os.path.join(c.data_path_LJSpeech, 'metadata.csv'),
                                  os.path.join(c.data_path_LJSpeech, 'wavs'),
                                  1,
                                  c.sample_rate,
                                  c.text_cleaner,
                                  c.num_mels,
                                  c.min_level_db,
                                  c.frame_shift_ms,
                                  c.frame_length_ms,
                                  c.preemphasis,
                                  c.ref_level_db,
                                  c.num_freq,
                                  c.power
                                  )

        # Test for batch size 1
        dataloader = DataLoader(dataset, batch_size=1,
                                shuffle=False, collate_fn=dataset.collate_fn,
                                drop_last=True, num_workers=c.num_loader_workers)

        for i, data in enumerate(dataloader):
            if i == self.max_loader_iter:
                break
            text_input = data[0]
            text_lengths = data[1]
            linear_input = data[2]
            mel_input = data[3]
            mel_lengths = data[4]
            stop_target = data[5]
            item_idx = data[6]

            # check the last time step to be zero padded
            assert mel_input[0, -1].sum() == 0
            assert mel_input[0, -2].sum() != 0
            assert linear_input[0, -1].sum() == 0
            assert linear_input[0, -2].sum() != 0
            assert stop_target[0, -1] == 1
            assert stop_target[0, -2] == 0
            assert stop_target.sum() == 1
            assert len(mel_lengths.shape) == 1
            assert mel_lengths[0] == mel_input[0].shape[0]

        # Test for batch size 2
        dataloader = DataLoader(dataset, batch_size=2,
                                shuffle=False, collate_fn=dataset.collate_fn,
                                drop_last=False, num_workers=c.num_loader_workers)

        for i, data in enumerate(dataloader):
            if i == self.max_loader_iter:
                break
            text_input = data[0]
            text_lengths = data[1]
            linear_input = data[2]
            mel_input = data[3]
            mel_lengths = data[4]
            stop_target = data[5]
            item_idx = data[6]

            if mel_lengths[0] > mel_lengths[1]:
                idx = 0
            else:
                idx = 1

            # check the first item in the batch
            assert mel_input[idx, -1].sum() == 0
            assert mel_input[idx, -2].sum() != 0, mel_input
            assert linear_input[idx, -1].sum() == 0
            assert linear_input[idx, -2].sum() != 0
            assert stop_target[idx, -1] == 1
            assert stop_target[idx, -2] == 0
            assert stop_target[idx].sum() == 1
            assert len(mel_lengths.shape) == 1
            assert mel_lengths[idx] == mel_input[idx].shape[0]

            # check the second itme in the batch
            assert mel_input[1-idx, -1].sum() == 0
            assert linear_input[1-idx, -1].sum() == 0
            assert stop_target[1-idx, -1] == 1
            assert len(mel_lengths.shape) == 1

            # check batch conditions
            assert (mel_input * stop_target.unsqueeze(2)).sum() == 0
            assert (linear_input * stop_target.unsqueeze(2)).sum() == 0

            
class TestTWEBDataset(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTWEBDataset, self).__init__(*args, **kwargs)
        self.max_loader_iter = 4

    def test_loader(self):
        dataset = TWEBDataset(os.path.join(c.data_path_TWEB, 'transcript.txt'),
                              os.path.join(c.data_path_TWEB, 'wavs'),
                              c.r,
                              c.sample_rate,
                              c.text_cleaner,
                              c.num_mels,
                              c.min_level_db,
                              c.frame_shift_ms,
                              c.frame_length_ms,
                              c.preemphasis,
                              c.ref_level_db,
                              c.num_freq,
                              c.power
                              )

        dataloader = DataLoader(dataset, batch_size=2,
                                shuffle=True, collate_fn=dataset.collate_fn,
                                drop_last=True, num_workers=c.num_loader_workers)

        for i, data in enumerate(dataloader):
            if i == self.max_loader_iter:
                break
            text_input = data[0]
            text_lengths = data[1]
            linear_input = data[2]
            mel_input = data[3]
            mel_lengths = data[4]
            stop_target = data[5]
            item_idx = data[6]

            neg_values = text_input[text_input < 0]
            check_count = len(neg_values)
            assert check_count == 0, \
                " !! Negative values in text_input: {}".format(check_count)
            # TODO: more assertion here
            assert linear_input.shape[0] == c.batch_size
            assert mel_input.shape[0] == c.batch_size
            assert mel_input.shape[2] == c.num_mels

    def test_padding(self):
        dataset = TWEBDataset(os.path.join(c.data_path_TWEB, 'transcript.txt'),
                              os.path.join(c.data_path_TWEB, 'wavs'),
                              1,
                              c.sample_rate,
                              c.text_cleaner,
                              c.num_mels,
                              c.min_level_db,
                              c.frame_shift_ms,
                              c.frame_length_ms,
                              c.preemphasis,
                              c.ref_level_db,
                              c.num_freq,
                              c.power
                              )

        # Test for batch size 1
        dataloader = DataLoader(dataset, batch_size=1,
                                shuffle=False, collate_fn=dataset.collate_fn,
                                drop_last=False, num_workers=c.num_loader_workers)

        for i, data in enumerate(dataloader):
            if i == self.max_loader_iter:
                break
                
            text_input = data[0]
            text_lengths = data[1]
            linear_input = data[2]
            mel_input = data[3]
            mel_lengths = data[4]
            stop_target = data[5]
            item_idx = data[6]

            # check the last time step to be zero padded
            assert mel_input[0, -1].sum() == 0
            assert mel_input[0, -2].sum() != 0, "{} -- {}".format(item_idx, i)
            assert linear_input[0, -1].sum() == 0
            assert linear_input[0, -2].sum() != 0
            assert stop_target[0, -1] == 1
            assert stop_target[0, -2] == 0
            assert stop_target.sum() == 1
            assert len(mel_lengths.shape) == 1
            assert mel_lengths[0] == mel_input[0].shape[0]

        # Test for batch size 2
        dataloader = DataLoader(dataset, batch_size=2,
                                shuffle=False, collate_fn=dataset.collate_fn,
                                drop_last=False, num_workers=c.num_loader_workers)

        for i, data in enumerate(dataloader):
            if i == self.max_loader_iter:
                break
            text_input = data[0]
            text_lengths = data[1]
            linear_input = data[2]
            mel_input = data[3]
            mel_lengths = data[4]
            stop_target = data[5]
            item_idx = data[6]

            if mel_lengths[0] > mel_lengths[1]:
                idx = 0
            else:
                idx = 1

            # check the first item in the batch
            assert mel_input[idx, -1].sum() == 0
            assert mel_input[idx, -2].sum() != 0, mel_input
            assert linear_input[idx, -1].sum() == 0
            assert linear_input[idx, -2].sum() != 0
            assert stop_target[idx, -1] == 1
            assert stop_target[idx, -2] == 0
            assert stop_target[idx].sum() == 1
            assert len(mel_lengths.shape) == 1
            assert mel_lengths[idx] == mel_input[idx].shape[0]

            # check the second itme in the batch
            assert mel_input[1-idx, -1].sum() == 0
            assert linear_input[1-idx, -1].sum() == 0
            assert stop_target[1-idx, -1] == 1
            assert len(mel_lengths.shape) == 1

            # check batch conditions
            assert (mel_input * stop_target.unsqueeze(2)).sum() == 0
            assert (linear_input * stop_target.unsqueeze(2)).sum() == 0

    
class TestTBPTT(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTBPTT, self).__init__(*args, **kwargs)
        self.max_loader_iter = 4

    def test_loader(self):
        dataset = LJSpeechDataset(os.path.join(c.data_path_LJSpeech, 'metadata.csv'),
                                  os.path.join(c.data_path_LJSpeech, 'wavs'),
                                  c.r,
                                  c.sample_rate,
                                  c.text_cleaner,
                                  c.num_mels,
                                  c.min_level_db,
                                  c.frame_shift_ms,
                                  c.frame_length_ms,
                                  c.preemphasis,
                                  c.ref_level_db,
                                  c.num_freq,
                                  c.power
                                  )

        dataloader = DataLoader(dataset, batch_size=c.batch_size,
                                shuffle=True, collate_fn=dataset.collate_fn,
                                drop_last=True, num_workers=c.num_loader_workers)
        
        tbp_size = 10
        for i, data in enumerate(dataloader):
            if i == self.max_loader_iter:
                break
            text_input = data[0]
            text_lengths = data[1]
            linear_input = data[2]
            mel_input = data[3]
            mel_lengths = data[4]
            stop_target = data[5]
            item_idx = data[6]
            
            # convert inputs to variables
            text_input_var = Variable(text_input)
            mel_spec_var = Variable(mel_input)
            mel_lengths_var = Variable(mel_lengths)
            linear_spec_var = Variable(linear_input, volatile=True)
            
            tbptt = TBPTT(text_input_var, mel_spec_var, linear_spec_var, mel_lengths_var, tbp_size)
            mel_test = []
            linear_test = []
            for text, mel, linear, lengths in tbptt:
                if tbptt.start:
                    assert text.shape[0] == c.batch_size, text.shape
                    assert mel.shape[0] == c.batch_size
                    assert mel.shape[1] == tbp_size, mel.shape
                    assert mel.shape[2] == c.num_mels
                
                # check the length consistency
                assert (mel.shape[1] >= lengths).all()
                for i, item in enumerate(mel):
                    length = lengths[i].data[0]
                    if item.shape[0] > length:
                        assert item.data[length:].sum() == 0
                mel_test.append(mel)
                linear_test.append(linear)
            mel_test = torch.cat(mel_test, 1)
            linear_test = torch.cat(linear_test, 1)
            assert (linear_input - linear_test.data).sum() == 0
            assert (mel_input - mel_test.data).sum() == 0
                

        