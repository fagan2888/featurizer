# -*- coding: utf-8 -*-
# Copyright StateOfTheArt.quant. 
#
# * Commercial Usage: please contact allen.across@gmail.com
# * Non-Commercial Usage:
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

from featurizer.interface import Functor
from featurizer.functions import time_series_functions as tsf

class ReturnsRollingStd(Functor):
    def __init__(self, window):
        self._window = window
    
    def forward(self, tensor):
        """input tensor is returns"""
        return tsf.rolling_std(tensor, window=self._window).squeeze(-1)

class Beta(Functor):
    def __init__(self, window=20):
        self._window = window

    def forward(self, tensor_x, tensor_y):
        if tensor_x.shape[-1] == 1:
            tensor_x = tensor_x.expand_as(tensor_y)
        output = tsf.rolling_cov(tensor_x, tensor_y, window=self._window) / tsf.rolling_var(tensor_x, window=self._window)
        return output

class Momentum(Functor):

    def __init__(self, window=5, lag_window=0):
        super(Momentum, self).__init__()
        self._window = window
        self._lag_window = lag_window

    def forward(self, tensor):
        """input is close"""
        tensor = tsf.pct_change(tensor, period=self._window)
        return tsf.shift(tensor, window=self._lag_window)

class BackwardSharpRatio(Functor):
    
    def __init__(self, window=30, lag_window=0):
        self._window = window
        self._lag_window = lag_window
    
    def forward(self, tensor):
        """defalt input is close"""
        returns = tsf.pct_change(tensor, period=1)
        sharp_ratio = tsf.rolling_mean_(returns, window=self._window) / tsf.rolling_std(returns, window=self._window)
        return tsf.shift(sharp_ratio, window=self._lag_window).squeeze(-1)


class AmihudRatio(Functor):
    def __init__(self, window =5):
        self._window = window
    
    def forward(self, tensor_x, tensor_y):
        """
        tensor_x is returns: sequence_window x order_book_ids
        tensor_y is turnover ratio: sequency_window x order_book_ids
        """
        output = abs(tensor_x) / tensor_y
        #pdb.set_trace()
        return tsf.rolling_mean_(output, window=self._window)

if __name__ == "__main__":
    import torch
    order_book_ids = 20
    sequence_window = 30
    
    # =========================================== #
    # test beta
    # =========================================== #
    returns_x = torch.randn(sequence_window, order_book_ids)
    returns_benchmark = torch.randn(sequence_window, 1)
    
    beta_functor = Beta(window=5)
    beta = beta_functor(returns_benchmark,returns_x)