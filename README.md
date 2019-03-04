# eye2mouth

## train
1. Put separated images into `input/image_top/` and `input/image_bottom`
2. Generate dataset by concatenating and resizing the images
~~~bash
$ python gen_dataset.py
~~~
3. Start training
~~~bash
$ python main.py --phase train --dataset_name face100 --batch_size 10 --fine_size 128
~~~

## test
1. Start testing
~~~bash
$ python main.py --phase test --dataset_name face100 --batch_size 10 --fine_size 128
~~~
