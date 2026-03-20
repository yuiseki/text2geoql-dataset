[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
