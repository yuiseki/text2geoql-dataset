[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Seodaemun-gu"]->.inner;
(
  nwr["amenity"="place_of_worship"](area.inner)(area.outer);
);
out geom;
