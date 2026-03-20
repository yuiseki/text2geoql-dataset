[out:json][timeout:30];
area["name:en"="Osaka Prefecture"]->.outer;
area["name:en"="Taisho Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="shinto"](area.inner)(area.outer);
);
out geom;
