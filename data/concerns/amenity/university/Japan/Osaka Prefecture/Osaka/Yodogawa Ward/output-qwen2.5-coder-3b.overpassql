[out:json][timeout:30];
area["name:en"="Yodogawa Ward"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
