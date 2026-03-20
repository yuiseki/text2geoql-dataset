[out:json][timeout:30];
area["name:en"="Chuo"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
