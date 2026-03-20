// Important note: Sushi shops are typically found in specific areas of Tokyo, such as the Tsukiji Fish Market.
[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Tama"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="sushi"](area.inner)(area.outer);
);
out geom;
