// Important note: Sushi shops are typically found in Japanese restaurants or markets.
[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Tachikawa"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"~"sushi"](area.inner)(area.outer);
);
out geom;
