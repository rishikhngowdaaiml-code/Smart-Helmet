import cv2
import albumentations as A
import os
import glob

# Module 9: AI Training Improvements
# This script demonstrates how to augment a YOLOv8 dataset to be robust 
# against helmet-mounted camera challenges (shake, motion blur, bad weather).

def get_augmentation_pipeline():
    return A.Compose([
        # Simulate camera shake & motion blur from head turns
        A.MotionBlur(blur_limit=(7, 15), p=0.4),
        A.GaussianBlur(blur_limit=(3, 7), p=0.2),
        A.Defocus(radius=(3, 6), alias_blur=(0.1, 0.5), p=0.2),
        
        # Simulate lighting issues & glare
        A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.5),
        A.CLAHE(clip_limit=4.0, tile_grid_size=(8, 8), p=0.3),
        A.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.1, p=0.3),
        
        # Simulate bad weather (rain/fog)
        A.RandomRain(brightness_coefficient=0.9, drop_width=1, blur_value=3, p=0.1),
        A.RandomFog(fog_coef_lower=0.1, fog_coef_upper=0.5, alpha_coef=0.08, p=0.1),
        
        # Spatial augmentations to simulate bumps/vibrations
        A.ShiftScaleRotate(shift_limit=0.06, scale_limit=0.1, rotate_limit=15, p=0.5),
        
        # Simulate partial occlusions (e.g. mud on lens or obstruction)
        A.CoarseDropout(max_holes=8, max_height=32, max_width=32, min_holes=1, min_height=8, min_width=8, fill_value=0, p=0.3)
    ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

def augment_dataset(image_dir, label_dir, output_image_dir, output_label_dir, num_augmentations=3):
    os.makedirs(output_image_dir, exist_ok=True)
    os.makedirs(output_label_dir, exist_ok=True)
    
    pipeline = get_augmentation_pipeline()
    
    image_paths = glob.glob(os.path.join(image_dir, "*.jpg"))
    
    for img_path in image_paths:
        base_name = os.path.basename(img_path)
        name, ext = os.path.splitext(base_name)
        label_path = os.path.join(label_dir, f"{name}.txt")
        
        if not os.path.exists(label_path):
            continue
            
        # Read image
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Read labels (YOLO format)
        bboxes = []
        class_labels = []
        with open(label_path, 'r') as f:
            for line in f.readlines():
                parts = line.strip().split()
                if len(parts) == 5:
                    class_labels.append(int(parts[0]))
                    bboxes.append([float(x) for x in parts[1:5]])
                    
        for i in range(num_augmentations):
            try:
                # Apply augmentations
                transformed = pipeline(image=image, bboxes=bboxes, class_labels=class_labels)
                transformed_image = transformed['image']
                transformed_bboxes = transformed['bboxes']
                transformed_labels = transformed['class_labels']
                
                # Save augmented image
                aug_img_name = f"{name}_aug_{i}{ext}"
                aug_img_path = os.path.join(output_image_dir, aug_img_name)
                cv2.imwrite(aug_img_path, cv2.cvtColor(transformed_image, cv2.COLOR_RGB2BGR))
                
                # Save augmented labels
                aug_label_name = f"{name}_aug_{i}.txt"
                aug_label_path = os.path.join(output_label_dir, aug_label_name)
                
                with open(aug_label_path, 'w') as f:
                    for bbox, label in zip(transformed_bboxes, transformed_labels):
                        f.write(f"{label} {' '.join(map(str, bbox))}\n")
                        
            except Exception as e:
                print(f"Error augmenting {img_path}: {e}")

if __name__ == "__main__":
    print("This script is intended to be run before training.")
    print("Example usage:")
    print("augment_dataset('dataset/images/train', 'dataset/labels/train', 'dataset_aug/images/train', 'dataset_aug/labels/train')")
