[out:json][timeout:30];
area["name:en"="Municipality of Prizren"]->.searchArea;
(
  nwr["building"="church"](area.searchArea);
  nwr["amenity"="place_of_worship"]["religion"="christian"](area.searchArea);
);
out geom;
