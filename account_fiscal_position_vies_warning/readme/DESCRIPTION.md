This module adds a verification on `res.partner` and `account.move` models 
ensuring that Fiscal positions with check Show Vies Warning can only be assigned to partners who have 
successfully passed VIES validation (vies_valid = True).