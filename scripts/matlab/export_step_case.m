% Simulate and export the instantaneous Step startup case.

script_dir = fileparts(mfilename("fullpath"));
project_root = fullfile(script_dir, "..", "..");

model_dir = fullfile(project_root, "models", "simulink");
addpath(model_dir);

model = "propellant_consuption_baseline";

if ~bdIsLoaded(model)
    load_system(model);
end

% Select the Step profile for this simulation.
sim_input = Simulink.SimulationInput(model);

sim_input = setBlockParameter( ...
    sim_input, ...
    model + "/Profile selector", ...
    "Value", "0");

sim_input = setModelParameter( ...
    sim_input, ...
    "StopTime", "stop_time_s");

out = sim(sim_input);

% Extract consumed-mass signals.
t = out.sim_total_mass.Time;
total_mass_kg = out.sim_total_mass.Data;
lox_mass_kg = out.sim_lox_mass.Data;
ch4_mass_kg = out.sim_ch4_mass.Data;

% Analytical expectations for instantaneous startup.
expected_duration_s = stop_time_s - start_time_s;

expected_masses_kg = expected_duration_s * ...
    [total_flow_kg_s, lox_flow_kg_s, ch4_flow_kg_s];

simulated_masses_kg = ...
    [total_mass_kg(end), lox_mass_kg(end), ch4_mass_kg(end)];

% Check the final simulation time.
assert(abs(t(end) - stop_time_s) < 1e-9, ...
    "The exported final time does not match stop_time_s.");

% Check each final mass against the Step analytical result.
mass_tolerance_kg = 1e-6 + 1e-8 * abs(expected_masses_kg);

assert(all(abs(simulated_masses_kg - expected_masses_kg) ...
    <= mass_tolerance_kg), ...
    "Step final masses do not match the analytical expectations.");

% Check mass balance throughout the simulation.
balance_error_kg = total_mass_kg - lox_mass_kg - ch4_mass_kg;

assert(all(abs(balance_error_kg(:)) ...
    <= 1e-6 + 1e-8 * abs(total_mass_kg(:))), ...
    "Step propellant mass balance failed.");

% Save separately from the historical baseline export.
profile_name = 'step';

output_dir = fullfile(project_root, "results", "matlab_simulink");

if ~isfolder(output_dir)
    mkdir(output_dir);
end

output_file = fullfile(output_dir, "step_export.mat");

save(output_file, ...
    "profile_name", ...
    "t", ...
    "total_mass_kg", ...
    "lox_mass_kg", ...
    "ch4_mass_kg", ...
    "total_flow_kg_s", ...
    "lox_flow_kg_s", ...
    "ch4_flow_kg_s", ...
    "start_time_s", ...
    "stop_time_s");

fprintf("\n--- STEP simulation results ---\n");
fprintf("Final total mass: %.4f kg\n", total_mass_kg(end));
fprintf("Final LOX mass:   %.4f kg\n", lox_mass_kg(end));
fprintf("Final CH4 mass:   %.4f kg\n", ch4_mass_kg(end));
fprintf("Step final mass checks: PASS\n");
fprintf("Step mass balance: PASS\n");
fprintf("Saved Step export: %s\n", output_file);