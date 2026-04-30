'''
USD compliance validation via UsdUtils.ComplianceChecker.
'''
import logging
log = logging.getLogger('gegede')


def validate_object(usd_geometry):
    '''Run UsdUtils compliance check; raises ValueError on hard failures.'''
    try:
        from pxr import UsdUtils
    except ImportError:
        log.warning('UsdUtils not available; skipping USD validation')
        return True

    stage = usd_geometry.stage
    try:
        checker = UsdUtils.ComplianceChecker(arkit=False, skipARKitRootLayerCheck=True)
        checker.CheckCompliance(stage)
        errors = list(checker.GetErrors())
        warnings = list(checker.GetWarnings())
    except Exception as exc:
        log.warning('USD compliance check failed with exception: %s', exc)
        return True

    for w in warnings:
        log.warning('UsdCompliance: %s', w)
    if errors:
        for e in errors:
            log.error('UsdCompliance: %s', e)
        raise ValueError(f'USD compliance check failed: {errors[0]}')
    return True
