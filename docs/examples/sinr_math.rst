SINR & Throughput Example
=========================

See :doc:`../user_guide/propagation_math` for equations.

.. code-block:: python

   import numpy as np
   from pytwinnet.accelerate.vectorized import fspl_matrix_db

   tx = np.array([[0,0,10]])
   rx = np.array([[50,0,1.5],[150,50,1.5]])
   f = 3.5e9
   pl = fspl_matrix_db(tx, rx, f)
   print("FSPL:", pl)
