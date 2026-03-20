[out:json][timeout:30];
area["name:en"="Higashisumiyoshi Ward"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
