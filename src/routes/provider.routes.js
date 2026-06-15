const router = require('express').Router();
const controller = require('../controllers/provider.controller');

router.get('/:provider/latest', controller.latest);
router.get('/:provider/search', controller.search);
router.get('/:provider/detail/:slug', controller.detail);
router.get('/:provider/episode/:slug', controller.episode);

module.exports = router;
