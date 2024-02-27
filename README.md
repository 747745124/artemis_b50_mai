### ARTEMIS Maimai B50 Generator

This is a simple tool for B50 (Best 50 scores) generator for those who use [ARTEMIS](https://gitea.tendokyu.moe/Hay1tsme/artemis) as their maimai server. It is based on maimaiDX and maibot project.

![image-20240225014842014](./README_images/image-20240225014842014.png)

> Sample image



#### To Use:

Make sure you are able to access the Artemis server. (At least READ access)

1. Assume Python environment is set up correctly (recommend to use venv), install dependencies

   ```shell
   pip install -r /path/to/requirements.txt
   ```

2. Download [image and font resources](https://drive.google.com/file/d/1Kl6dZVPR60DWcQqbtITeXAMnsK4ZTjes/view?usp=sharing), place the folder with below hierarchy.![image-20240225015600208](./README_images/image-20240225015600208.png)

> All copyrights belongs to SEGA. Please delete the files within 24 hours after download.

3. (Optional) Run `dx_score_gen.py` to preprocess the xml files to generate `md_cache.json`

* This files contains dx score information for each chart.
* A preprocessed version is provided

4. Change parameters in `gen_rating_artemis.py`

* database host / password

* Artemis game version

* `display_name`

* `use_theme`

* `use_alt` (layout)

5. Run `gen_rating_artemis.py`

* by default the result image is under the root folder



#### Ref:

https://github.com/Diving-Fish/mai-bot

https://gitea.tendokyu.moe/Hay1tsme/artemis

https://github.com/Yuri-YuzuChaN/maimaiDX