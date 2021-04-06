from selenium import webdriver
import pandas as pd

url = 'https://www.youtube.com/c/HealthyPockets/videos'
webPage='https://www.youtube.com/c/KikeJav/videos'

# PATH=r"C:\Users\gio-v\Documents\UOC\Tipologiayciclodevidadelosdatos\chromedriver.exe"
PATH=r"C:\Users\ASUS X555B\Documents\UOC\Tipología de Datos\chromedriver.exe"

driver = webdriver.Chrome(PATH)
driver.get(url)

videos = driver.find_elements_by_class_name('style-scope ytd-grid-video-renderer')
#videos = driver.find_elements_by_id('items')
#videos = driver.find_elements_by_xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-grid-renderer/div[1]/ytd-grid-video-renderer[1]/div[1]/div[1]')

video_list = []
for video in videos:
    title = video.find_element_by_xpath('.//*[@id="video-title"]').text
    views = video.find_element_by_xpath('.//*[@id="metadata-line"]/span[1]').text
    when = video.find_element_by_xpath('.//*[@id="metadata-line"]/span[2]').text
    vid_item = {
        'title' : title,
        'views' : views,
        'posted' : when,
    }
    video_list.append(vid_item)


df = pd.DataFrame(video_list)
print(df)
