1. Create a tax group named **"Ecotaxes"**. The sequence must be lower than other tax groups.
   - Set the **Preceding Subtotal** field to **"Without Ecotax"**.

2. Create two taxes named **"Fixed Ecotax"** and **"Weight-Based Ecotax"**.
   - Check the **Ecotax** checkbox.
   - Set the correct Python code:

     - For the fixed ecotax:

       .. code-block:: python

          result = quantity and product.fixed_ecotax * quantity or 0.0

     - For the weight-based ecotax:

       .. code-block:: python

          result = quantity and product.weight_based_ecotax * quantity or 0.0

   - Check the **Included in Base Amount** option.
   - The sequence for Ecotax must be lower than the VAT tax.

3. For VAT taxes, check the **Base Affected by Previous Taxes?** option.

4. Add an ecotax classification via the menu **Accounting > Configuration > Taxes > Ecotax Classification**.

   - The ecotax classification can be either a fixed ecotax or a weight-based ecotax.
   - Ecotax classification information can be used for legal declarations.
   - For the fixed ecotax, the ecotax amount is used as a default value, which can be overridden on the product.
   - For the weight-based ecotax, define one ecotax by a coefficient applied to the weight (depending on the product's materials).
   - Set the appropriate tax in the **Sale Ecotax** field.

5. Assign one or more ecotax classifications to a product.

   - The ecotax amount can also be manually overridden on the product.
