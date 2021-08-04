import numpy as np
import pandas as pd
import os
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern
from modAL.models import ActiveLearner


'''
All functions are written for 3D features. Change as required for your data.
'''

def sample_initial_training_points(data, features, label):
    ''' Creates labeled data and query pool from given data'''
    X_raw = np.stack((data[features[0]].astype('float'), 
                      data[features[1]].astype('float'), 
                      data[features[2]].astype('float')), axis=-1)
    y_raw = np.array(data[label].astype('float'))

    # Initial training points
    n_labeled_examples = X_raw.shape[0]
    training_indices = np.random.randint(low=0, high=n_labeled_examples, size=3)

    X_train = X_raw[training_indices]
    y_train = y_raw[training_indices]

    # Isolate the training examples from the query pool
    X_pool = np.delete(X_raw, training_indices, axis=0)
    y_pool = np.delete(y_raw, training_indices, axis=0)

    #return labeled training points and pool
    return X_train, y_train, X_pool, y_pool


def GP_regression_std(regressor, X):
    '''Uncertainty sampling'''
    _, std = regressor.predict(X, return_std=True)
    query_idx = np.argmax(std)
    return query_idx, X[query_idx]


def GP_softmax(regressor, X):
    '''Uncertainty sampling with softmax probabilities.'''
    _, std = regressor.predict(X, return_std=True)
    t = 1 
    p = np.exp(std/t)/np.sum(np.exp(std/t))  
    query_idx = np.argmax(np.random.multinomial(1, p, 1))
    return query_idx, X[query_idx]


def active_learner(X_train, y_train):
    '''Active learner with gaussian process regression'''
    kernel = Matern(length_scale=[0.1, 0.1, 0.1]) 
    regressor = GaussianProcessRegressor(kernel=kernel, normalize_y=True, n_restarts_optimizer=64)
    regressor_3d = ActiveLearner(
        estimator=regressor,
        query_strategy= GP_softmax,
        X_training=X_train, y_training=y_train
    )
    return regressor_3d


def query_data(N_QUERIES, X_pool, y_pool, regressor_3d, X_test = None, y_test = None):
    '''Query instances from the pool'''
    Xs = np.empty((1,3))
    ys = np.empty((1))
    model_accuracy = []
    # Allow our model to query our unlabeled dataset for the most
    # informative points according to our query strategy (uncertainty sampling).
    for index in range(N_QUERIES):
        query_index, query_instance = regressor_3d.query(X_pool)
        # Teach our ActiveLearner model the record it has requested.
        X, y = X_pool[query_index].reshape(-1, 3), y_pool[query_index].reshape(1, )
        
        # For CFD on the fly, uncomment the respective lines for 
        # bent pipe or expansion joint below
        # X = X_pool[query_index].reshape(-1, 3)
        # y = run_bent_pipe_model(pipe_D=X[0], bend_angle=np.rad2deg(X[1]), 
        #                         inlet_v=X[2], rho=998., muo=0.009373)['Del P/L']
        # y = run_expansion_model(inlet_D=X[0], expansion_angle=np.rad2deg(X[1]), 
        #                         inlet_v=X[2], rho=1060., muo=0.004)['Backflow Percent']
        
        regressor_3d.teach(X=X, y=y)
        # Remove the queried instance from the unlabeled pool.
        Xs = np.append(Xs, X, axis=0)
        ys = np.append(ys, y, axis=0)
        X_pool, y_pool = np.delete(X_pool, query_index, axis=0), np.delete(y_pool, query_index)
    return Xs[1:], ys[1:], X_pool, y_pool


def create_train_dat(directory, Xs, ys, features, label, density=998., viscosity=0.0009737):
    '''Create train.dat and input file for SISSO'''
    if not os.path.exists(directory):
        os.makedirs(directory)
    df = pd.DataFrame.from_dict({features[0]: Xs[:,0], features[1]: Xs[:, 1], features[2]: Xs[:, 2], label: ys})
    df['Density'] = np.ones(df.shape[0]) * density
    df['Viscosity'] = np.ones(df.shape[0]) * viscosity

    df.to_csv(directory + 'train.dat', sep=' ', 
                  columns=[label, *features, 'Density', 'Viscosity'],
                  index=True, index_label='materials')
    sisso = f'''!_________________________________________________________________
! keywords for the target properties
!_________________________________________________________________
ptype=1
ntask=1
nsample={df.shape[0]}                           ! number of samples for each task
task_weighting=1
desc_dim=3                            ! dimension of the descriptor
restart=.false.                       ! set .true. to continue a job that was stopped but not yet finished
!_________________________________________________________________
!keywords for feature construction and sure independence screening
!_________________________________________________________________
nsf=5                                 ! number of scalar features (one feature is one number for each material)
rung=2                                ! rung (<=3) of the feature space to be constructed (times of applying the opset recursively)
opset='(+)(-)(*)(/)(exp)(exp-)(sin)(cos)'
maxcomplexity=5                      ! max feature complexity (number of operators in a feature)
dimclass=(1:1)(2:2)(3:3)(4:5)              ! group features according to their dimension/unit; those not in any () are dimensionless
maxfval_lb=1e-6                       ! features having the max. abs. data value < maxfval_lb will not be selected
maxfval_ub=1e4                        ! features having the max. abs. data value > maxfval_ub will not be selected
subs_sis=2000                          ! size of the SIS-selected (single) subspace for each descriptor dimension
!_________________________________________________________________
!keywords for descriptor identification via a sparsifying operator
!_________________________________________________________________
method='L0'                           ! sparsification operator: 'L1L0' or 'L0'; L0 is recommended!
fit_intercept=.false.                 ! fit to a nonzero intercept (.true.) or force the intercept to zero (.false.)
metric='RMSE'                         ! for regression only, the metric for model selection: RMSE,MaxAE
nm_output=100                          ! number of the best models to output'''

    with open(directory + 'SISSO.in', 'w') as f:
        f.write(sisso)
    
    return directory


def create_test_dat(directory, test_data):
    test_data.to_csv(directory + 'test.dat', index=True, index_label='materials')
    return
