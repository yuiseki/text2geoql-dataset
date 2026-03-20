[out:json][timeout:30];
area["name:en"="Suginami"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
