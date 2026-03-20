// Important note: Sushi shops are typically found in specific areas of Shibuya.
[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Shibuya"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="sushi"](area.inner)(area.outer);
);
out geom;
