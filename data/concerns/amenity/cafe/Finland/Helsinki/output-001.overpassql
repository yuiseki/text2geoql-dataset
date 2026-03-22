[out:json][timeout:30];
area["name:en"="Helsinki"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;