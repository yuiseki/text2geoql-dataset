[out:json][timeout:30];
area["name:en"="Municipality of Prizren"]->.searchArea;
(
  nwr["amenity"="bar"](area.searchArea);
);
out geom;
