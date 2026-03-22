[out:json][timeout:30];
area["name:en"="Casablanca"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;