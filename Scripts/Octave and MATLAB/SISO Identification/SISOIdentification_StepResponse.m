%Copyright 2022 Leonardo Cabral
%
%Permission is hereby granted, free of charge, to any person obtaining a copy
%of this software and associated documentation files (the "Software"), to deal
%in the Software without restriction, including without limitation the rights
%to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
%copies of the Software, and to permit persons to whom the Software is
%furnished to do so, subject to the following conditions:
%
%The above copyright notice and this permission notice shall be included in all
%copies or substantial portions of the Software.
%
%THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
%IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
%FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
%AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
%LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
%OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
%SOFTWARE.

%% Script description
% Plots the step response considering TeCoLab as a SISO system. The input is the
% sum of both actuators (i.e. heaters), presented as a percentage of maximum
% power. The output is the mean of both temperature sensors minus the ambient
% temperature. Moreover, the offset between the output and the ambient
% temperature is mitigated by subtracting the first sample of the output from
% output vector.

%% Initialize workspace
clear all
close all
clc

%% Load Octave packages
if (exist('OCTAVE_VERSION', 'builtin'))
  pkg load control
end

%% Get experiment log file
[logname, logpath, ~] = uigetfile();
fullpath =  [logpath, logname];
expdata = csvread(fullpath);
expdata = expdata(2:end, :);

%% Data pre processesment
stepresponse.time = expdata(:,1)/1000;
stepresponse.input.data = 100*(expdata(:, 25) + expdata(:, 26))/200;
stepresponse.output.data = (expdata(:,2) + expdata(:,3))/2 - expdata(:,4);
% Remove offset between amb. temp. and initial out.
stepresponse.output.data = stepresponse.output.data - stepresponse.output.data(1);

%% Get first order system parameters
onindex = find(diff(stepresponse.input.data) > 0) + 1;
stepresponse.input.onTime = stepresponse.time(onindex);
stepresponse.input.onAmplitude = stepresponse.input.data(onindex);
clear onindex

delayindex = find(stepresponse.output.data >= 0.5, 1);
stepresponse.output.onDelayTime = stepresponse.time(delayindex) - stepresponse.input.onTime;
stepresponse.output.onFinalValue = stepresponse.output.data(end);
stepresponse.output.onTimeConstant = stepresponse.time(find(stepresponse.output.data >= (1-exp(-1))*stepresponse.output.onFinalValue, 1)) - stepresponse.input.onTime - stepresponse.output.onDelayTime;
clear delayindex

stepresponse.system.timeConstant = stepresponse.output.onTimeConstant;
stepresponse.system.transportDelay = stepresponse.output.onDelayTime;
stepresponse.system.staticGain = stepresponse.output.onFinalValue / stepresponse.input.onAmplitude;

disp('Step Response Information:')
disp(stepresponse.system)

%% Plot input and output
figure(1)
set(gcf, 'Position', get(0, 'Screensize'));
subplot(2,1,1)
plot(stepresponse.time, stepresponse.input.data, 'linewidth', 2, 'color', 'blue');
grid on; hold on;
title('Step Response Identification', 'fontsize', 22, 'interpreter', 'latex')
xlabel('Time [s]', 'fontsize', 18, 'interpreter', 'latex')
ylabel('Applied Power [%]', 'fontsize', 18, 'interpreter', 'latex')
set(gca, 'XTickLabel', get(gca, 'XTickLabel'), 'fontsize', 14)
ylim([0 1.2*max(stepresponse.input.data)])
xlim([0 stepresponse.time(end)])
subplot(2,1,2)
plot(stepresponse.time, stepresponse.output.data, 'linewidth', 2, 'color', 'blue');
grid on; hold on;

% Plot step response of the model
s = tf('s')
G = stepresponse.system.staticGain/(s*stepresponse.system.timeConstant + 1)
simtime = [0 : 0.1 : stepresponse.time(end)];
siminput = zeros(size(simtime));
siminput(find(simtime >= stepresponse.input.onTime)) = stepresponse.input.onAmplitude;
[simout, simtime, ~] = lsim(G, siminput, simtime + stepresponse.output.onDelayTime);
simtime = [0; simtime]; simout = [0; simout];
plot(simtime, simout, 'linewidth', 2, 'color', 'red')

% Plot the rest of the figure
plot([0 stepresponse.time(end)], [stepresponse.output.onFinalValue stepresponse.output.onFinalValue], 'color', [0.5 0.5 0.5])
plot([stepresponse.output.onTimeConstant+stepresponse.input.onTime+stepresponse.output.onDelayTime stepresponse.output.onTimeConstant+stepresponse.input.onTime+stepresponse.output.onDelayTime], [0 stepresponse.output.data(find(stepresponse.output.data >= (1-exp(-1))*stepresponse.output.onFinalValue, 1))], 'color', [0.5 0.5 0.5])
plot([0 stepresponse.output.onTimeConstant+stepresponse.input.onTime+stepresponse.output.onDelayTime], [stepresponse.output.data(find(stepresponse.output.data >= (1-exp(-1))*stepresponse.output.onFinalValue, 1)) stepresponse.output.data(find(stepresponse.output.data >= (1-exp(-1))*stepresponse.output.onFinalValue, 1))], 'color', [0.5 0.5 0.5])
plot([stepresponse.input.onTime stepresponse.input.onTime], [0 1.2*max(stepresponse.output.data)], 'color', [0.5 0.5 0.5])
plot([stepresponse.input.onTime+stepresponse.output.onDelayTime stepresponse.input.onTime+stepresponse.output.onDelayTime], [0 1.2*max(stepresponse.output.data)], 'color', [0.5 0.5 0.5])
xlabel('Time [s]', 'fontsize', 18, 'interpreter', 'latex')
ylabel('Output Temperature [°C]', 'fontsize', 18, 'interpreter', 'latex')
set(gca, 'XTickLabel', get(gca, 'XTickLabel'), 'fontsize', 14)
ylim([0 1.2*max(stepresponse.output.data)])
xlim([0 stepresponse.time(end)])

% Plot legend
legend('Experimental step response', 'First order with delay step response')

