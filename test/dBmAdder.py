import numpy as np

def dbm_to_mw(dbm):
    """Convert dBm to mW"""
    return 10 ** (dbm / 10)

def mw_to_dbm(mw):
    """Convert mW to dBm"""
    if mw == 0:
        return float('-inf')  # log(0) is -inf
    return 10 * np.log10(mw)

def add_dbm_array(dbm_array):
    """Add an array of dBm values correctly"""
    total_mw = np.sum(dbm_to_mw(dbm_array))
    return mw_to_dbm(total_mw)

# Example usage
dbm_values = np.array([4, 3.6,3.1,2.66,2.57,2.4,2.3,3,3])+20-4  # Example dBm values
dbm_values = np.array([1,1,1,0.5,0.1,0,0,0,0])+20 # Example dBm values
dbm_values = np.array([1,1,1,1,0.7,0.8,0.6,0.4,0])+20 # Example dBm values
total_dbm = add_dbm_array(dbm_values)

print(f"Total power in dBm: {total_dbm:.2f}")
