[out:json][timeout:30];
area["name:en"="Casablanca"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;