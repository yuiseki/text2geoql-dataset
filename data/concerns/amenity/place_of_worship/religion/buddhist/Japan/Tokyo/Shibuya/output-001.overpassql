[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Shibuya"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="buddhist"](area.inner)(area.outer);
);
out geom;
