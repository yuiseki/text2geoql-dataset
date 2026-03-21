[out:json][timeout:30];
area["name:en"="Sham Shui Po District"]->.outer;
(
  nwr["amenity"~"restaurant"]["cuisine"~"korean"](area.outer);
);
out geom;
