#!/usr/bin/env python
"""
Downloads the raw data from W&B then cleans it using very basic EDA steps. After, the cleaned is saved to W&B
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Get the data
    logger.info('Getting the data')
    local_path = run.use_artifact(args.input_artifact).file()
    data = pd.read_csv(local_path)

    # Clean the data
    logger.info('Cleaning the data by removing outliers')
    temp_idx = data['price'].between(args.min_price, args.max_price)
    new_data = data[temp_idx].copy()

    temp_idx = new_data['longitude'].between(-74.25, -73.50) & new_data['latitude'].between(40.5, 41.2)
    new_data = new_data[temp_idx].copy()

    # Save new data
    logger.info('Saving cleaned data')
    new_data.to_csv('clean_sample.csv', index=False)

    # Creating artifact for it
    logger.info('Creating artifact')
    artifact = wandb.Artifact(args.output_artifact,
                             type=args.output_type, 
                             description=args.output_description)
    
    logger.info('Loading cleaned data into artifact')
    artifact.add_file('clean_sample.csv')

    logger.info('Logging artifact into W&B')
    run.log_artifact(artifact)

    logger.info('Finishing the run')
    run.finish()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="The input you want preprocessed",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="The output of the process",
        required=True,
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="The type of the output",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="The description of the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="lower limit of price column",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="upper limit of price column",
        required=True
    )


    args = parser.parse_args()

    go(args)
