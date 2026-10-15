script_dir = fileparts(mfilename("fullpath"));
project_root = fullfile(script_dir, "..", "..");
model_dir = fullfile(project_root, "models", "simulink");

addpath(model_dir);

model = "propellant_consuption_baseline";

if ~bdIsLoaded(model)
    load_system(model);
end
out = sim(model_name);

% Extract time and consumed-mass signals from To Workspace outputs.
t = out.sim_total_mass.Time;
total_mass_kg = out.sim_total_mass.Data;
lox_mass_kg = out.sim_lox_mass.Data;
ch4_mass_kg = out.sim_ch4_mass.Data;

% Export the nominal conditions used by the model.
total_flow_kg_s = total_flow_kg_s;
lox_flow_kg_s = lox_flow_kg_s;
ch4_flow_kg_s = ch4_flow_kg_s;
start_time_s = start_time_s;
ramp_duration_s = ramp_duration_s;
stop_time_s = stop_time_s;

% Save a portable analysis file in the project results directory.
output_dir = fullfile("results", "matlab_simulink");
if ~isfolder(output_dir)
    mkdir(output_dir);
end

output_file = fullfile(output_dir, "ramp_export.mat");
save(output_file, ...
    "t", ...
    "total_mass_kg", ...
    "lox_mass_kg", ...
    "ch4_mass_kg", ...
    "total_flow_kg_s", ...
    "lox_flow_kg_s", ...
    "ch4_flow_kg_s", ...
    "start_time_s", ...
    "ramp_duration_s", ...
    "stop_time_s");

fprintf("Saved ramp-case export: %s\n", output_file);