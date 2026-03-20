[out:json][timeout:30];
area["name:en"="Hyogo Prefecture"]->.outer;
area["name:en"="Kobe"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="shinto"](area.inner)(area.outer);
);
out geom;
