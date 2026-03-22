[out:json][timeout:30];
area["name:en"="Delhi"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;