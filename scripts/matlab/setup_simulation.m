% Engine parameters
thrust_N = 100000;   % Thrust [N]
isp_s = 350;         % Specific impulse [s]
g0_m_s2 = 9.80665;   % Standard gravity [m/s^2]
of_ratio = 3.5;      % LOX-to-CH4 mass ratio

% Simplified time profile
start_time_s = 1;      % Idealized startup time [s]
ramp_duration_s = 0.5; % Time to reach nominal flow [s]
stop_time_s = 10;      % Simulation end time [s]

% Mass flow rates [kg/s]
total_flow_kg_s = thrust_N / (isp_s * g0_m_s2);
lox_flow_kg_s = total_flow_kg_s * of_ratio / (1 + of_ratio);
ch4_flow_kg_s = total_flow_kg_s / (1 + of_ratio);

% Effective operating duration and consumed propellant mass [kg]
burn_duration_s = stop_time_s - start_time_s;
equivalent_full_flow_duration_s = burn_duration_s - ramp_duration_s /2;


total_mass_kg = total_flow_kg_s * equivalent_full_flow_duration_s;
lox_mass_kg = lox_flow_kg_s * equivalent_full_flow_duration_s;
ch4_mass_kg = ch4_flow_kg_s * equivalent_full_flow_duration_s;

% Basic model checks 
assert(thrust_N > 0, 'Thrust must be positive');
assert(isp_s > 0, 'Specific impulse must be positive');
assert(of_ratio > 0, 'O/F ratio must be positive');
assert(stop_time_s > start_time_s, ...
    'Stop time must be greater than startup time');
assert(ramp_duration_s > 0,...
    'Ramp duration must be positive');
assert(stop_time_s > start_time_s + ramp_duration_s, ...
    'Stop time must be grater than ramp end time.');

% Check propellant mass balance
mass_balance_error_kg = total_mass_kg - (lox_mass_kg + ch4_mass_kg);
assert(abs(mass_balance_error_kg)<1e-9,...
    'LOX and CH4 masses do not match total propellant mass.');

% Display calculated results 
fprintf('Total propellant mass: %.3f kg\n', total_mass_kg);
fprintf('LOX mass: %.3f kg\n', lox_mass_kg);
fprintf('CH4 mass: %.3f kg\n', ch4_mass_kg);
fprintf('Mass balance error: %.3e kg\n', mass_balance_error_kg);

% Thrust and total-impulse reference values.
% Assumption: constant specific impulse throughout the prescribed profile.
effective_exhaust_velocity_m_s = isp_s * g0_m_s2;

expected_step_impulse_N_s = thrust_N * burn_duration_s;
expected_ramp_impulse_N_s = thrust_N * equivalent_full_flow_duration_s;

fprintf('\n--- Thrust and impulse reference values ---\n');
fprintf('Nominal thrust: %.1f N\n', thrust_N);
fprintf('Effective exhaust velocity: %.3f m/s\n', effective_exhaust_velocity_m_s);
fprintf('Expected Step total impulse: %.1f N*s\n', expected_step_impulse_N_s);
fprintf('Expected ramp total impulse: %.1f N*s\n', expected_ramp_impulse_N_s);
