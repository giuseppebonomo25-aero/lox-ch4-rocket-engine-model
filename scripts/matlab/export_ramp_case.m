% Simulate and export the prescribed linear startup-ramp case.
%
% The output path is resolved relative to this script.
% Assumption: constant specific impulse throughout the prescribed profile.

script_dir = fileparts(mfilename("fullpath"));
project_root = fullfile(script_dir, "..", "..");
model_dir = fullfile(project_root, "models", "simulink");
addpath(model_dir);

model = "propellant_consuption_baseline";

if ~bdIsLoaded(model)
    load_system(model);
end

% Select the ramp profile explicitly.
sim_input = Simulink.SimulationInput(model);

sim_input = setBlockParameter( ...
    sim_input, ...
    model + "/Profile selector", ...
    "Value", "1");

sim_input = setModelParameter( ...
    sim_input, ...
    "StopTime", "stop_time_s");

out = sim(sim_input);

% Extract consumed-mass signals.
t = out.sim_total_mass.Time;
total_mass_kg = out.sim_total_mass.Data;
lox_mass_kg = out.sim_lox_mass.Data;
ch4_mass_kg = out.sim_ch4_mass.Data;

% Extract thrust and accumulated impulse.
thrust_time_s = out.sim_thrust.Time;
thrust_N_series = out.sim_thrust.Data;

impulse_time_s = out.sim_impulse.Time;
impulse_N_s_series = out.sim_impulse.Data;

% Analytical references.
% This expression assumes that the ramp finishes before simulation ends.
assert(ramp_duration_s > 0, ...
    'Ramp duration must be positive.');

assert(stop_time_s > start_time_s + ramp_duration_s, ...
    'The reference calculation requires the ramp to finish before stop time.');

expected_full_flow_duration_s = ...
    stop_time_s - start_time_s - ramp_duration_s / 2;

expected_masses_kg = expected_full_flow_duration_s * ...
    [total_flow_kg_s, lox_flow_kg_s, ch4_flow_kg_s];

simulated_masses_kg = ...
    [total_mass_kg(end), lox_mass_kg(end), ch4_mass_kg(end)];

expected_final_impulse_N_s = ...
    thrust_N * expected_full_flow_duration_s;

% Check final times.
assert(abs(t(end) - stop_time_s) < 1e-9, ...
    'The final mass-signal time does not match stop_time_s.');

assert(abs(thrust_time_s(end) - stop_time_s) < 1e-9, ...
    'The final thrust-signal time does not match stop_time_s.');

assert(abs(impulse_time_s(end) - stop_time_s) < 1e-9, ...
    'The final impulse-signal time does not match stop_time_s.');

% Check each final consumed mass.
mass_tolerance_kg = 1e-6 + 1e-8 * abs(expected_masses_kg);

assert(all(abs(simulated_masses_kg - expected_masses_kg) ...
    <= mass_tolerance_kg), ...
    'Ramp final masses do not match the analytical expectations.');

% Check mass balance throughout the exported series.
assert(isequal(size(total_mass_kg), size(lox_mass_kg), size(ch4_mass_kg)), ...
    'Consumed-mass signals must have matching dimensions.');

balance_error_kg = total_mass_kg - lox_mass_kg - ch4_mass_kg;

assert(all(abs(balance_error_kg(:)) ...
    <= 1e-6 + 1e-8 * abs(total_mass_kg(:))), ...
    'Ramp propellant mass balance failed.');

% Check maximum thrust.
thrust_tolerance_N = 1e-6 + 1e-8 * abs(thrust_N);

assert(abs(max(thrust_N_series(:)) - thrust_N) ...
    <= thrust_tolerance_N, ...
    'Ramp maximum thrust does not match nominal thrust.');

% Check final accumulated impulse.
impulse_tolerance_N_s = ...
    1e-6 + 1e-8 * abs(expected_final_impulse_N_s);

assert(abs(impulse_N_s_series(end) - expected_final_impulse_N_s) ...
    <= impulse_tolerance_N_s, ...
    'Ramp final impulse does not match the analytical expectation.');

% Save only after the checks pass.
% Use a character array for compatibility with the SciPy workflow.
profile_name = 'ramp';

output_dir = fullfile(project_root, "results", "matlab_simulink");

if ~isfolder(output_dir)
    mkdir(output_dir);
end

output_file = fullfile(output_dir, "ramp_export.mat");

save(output_file, ...
    'profile_name', ...
    't', ...
    'total_mass_kg', ...
    'lox_mass_kg', ...
    'ch4_mass_kg', ...
    'total_flow_kg_s', ...
    'lox_flow_kg_s', ...
    'ch4_flow_kg_s', ...
    'thrust_time_s', ...
    'thrust_N_series', ...
    'impulse_time_s', ...
    'impulse_N_s_series', ...
    'thrust_N', ...
    'isp_s', ...
    'g0_m_s2', ...
    'start_time_s', ...
    'ramp_duration_s', ...
    'stop_time_s');

fprintf('\n--- RAMP simulation results ---\n');
fprintf('Final total mass: %.4f kg\n', total_mass_kg(end));
fprintf('Final LOX mass:   %.4f kg\n', lox_mass_kg(end));
fprintf('Final CH4 mass:   %.4f kg\n', ch4_mass_kg(end));
fprintf('Maximum thrust:  %.3f N\n', max(thrust_N_series(:)));
fprintf('Final impulse:   %.3f N*s\n', impulse_N_s_series(end));
fprintf('Expected impulse: %.3f N*s\n', expected_final_impulse_N_s);
fprintf('Ramp final mass checks: PASS\n');
fprintf('Ramp mass balance: PASS\n');
fprintf('Ramp maximum thrust and final impulse checks: PASS\n');
fprintf('Saved ramp-case export: %s\n', output_file);