[out:json][timeout:30];
area["name:en"="Higashiyamato"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
