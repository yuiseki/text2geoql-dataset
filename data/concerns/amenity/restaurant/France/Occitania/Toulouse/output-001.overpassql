[out:json][timeout:30];
area["name:en"="Occitania"]->.outer;
area["name:en"="Toulouse"]->.inner;
(
  nwr["amenity"="restaurant"](area.inner)(area.outer);
);
out geom;