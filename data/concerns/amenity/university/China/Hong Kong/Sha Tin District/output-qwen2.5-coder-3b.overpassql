[out:json][timeout:30];
area["name:en"="Sha Tin District"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
